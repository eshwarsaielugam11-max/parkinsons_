"""
Unit and Integration Tests for Audio Preprocessing Pipeline.
Validates VAD, Resampling, Quality Checking, Normalization, and Fold-Local Fitting.
"""

import unittest
import numpy as np
from pathlib import Path
import sys
import os

# Ensure model root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.src.preprocessing.resample import resample_audio, to_mono
from model.src.preprocessing.vad import detect_voice_activity, trim_silence
from model.src.preprocessing.quality_check import (
    compute_clipping_ratio,
    estimate_snr_db,
    compute_quality_score
)
from model.src.preprocessing.normalize import (
    normalize_loudness,
    compute_fold_normalization_stats
)
from model.src.preprocessing.pipeline import preprocess_recording


class TestAudioPreprocessing(unittest.TestCase):

    def setUp(self):
        self.sr = 16000
        self.duration = 2.0  # seconds
        t = np.linspace(0, self.duration, int(self.sr * self.duration), endpoint=False)
        # 440 Hz pure sine wave with moderate amplitude (0.6)
        self.clean_tone = (0.6 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    def test_silent_input_is_flagged(self):
        """Verify silent input receives low/zero quality score and is rejected."""
        silent_audio = np.zeros(int(self.sr * 2.0), dtype=np.float32)
        quality = compute_quality_score(silent_audio, sr=self.sr)
        
        self.assertFalse(quality["is_acceptable"], "Silent audio should not be marked acceptable.")
        self.assertEqual(quality["audio_quality_score"], 0.0)
        self.assertIn("SILENT_OR_EMPTY_AUDIO", quality["rejection_reasons"])
        
        # Test through unified pipeline
        result = preprocess_recording(silent_audio, orig_sr=self.sr)
        self.assertFalse(result["is_acceptable"])

    def test_clipped_input_is_flagged(self):
        """Verify severely clipped audio is flagged with high clipping ratio."""
        # Create heavily clipped signal (square/saturated waveform)
        clipped_audio = np.clip(self.clean_tone * 5.0, -1.0, 1.0)
        clip_ratio = compute_clipping_ratio(clipped_audio, threshold=0.999)
        self.assertGreater(clip_ratio, 0.10, "Clipped test signal must have clipping ratio > 10%.")
        
        quality = compute_quality_score(clipped_audio, sr=self.sr)
        self.assertFalse(quality["is_acceptable"], "Severely clipped audio should be rejected.")
        self.assertTrue(any("HIGH_CLIPPING" in r for r in quality["rejection_reasons"]))

    def test_known_good_synthetic_tone_passes(self):
        """Verify clean synthetic speech-range tone passes quality checks."""
        quality = compute_quality_score(self.clean_tone, sr=self.sr)
        self.assertTrue(quality["is_acceptable"], f"Clean tone failed QA: {quality['rejection_reasons']}")
        self.assertGreaterEqual(quality["audio_quality_score"], 0.60)
        self.assertEqual(quality["clipping_ratio"], 0.0)
        self.assertGreater(quality["estimated_snr_db"], 10.0)

    def test_resampling_target_sample_rate(self):
        """Verify resampling produces exact target sample rate and correct shape."""
        orig_sr = 44100
        t = np.linspace(0, 1.5, int(orig_sr * 1.5), endpoint=False)
        audio_44k = (0.5 * np.sin(2 * np.pi * 300.0 * t)).astype(np.float32)
        
        target_sr = 16000
        resampled, out_sr = resample_audio(audio_44k, orig_sr=orig_sr, target_sr=target_sr)
        
        self.assertEqual(out_sr, target_sr)
        expected_len = int(round(1.5 * target_sr))
        self.assertAlmostEqual(len(resampled), expected_len, delta=5)

    def test_multi_channel_to_mono(self):
        """Verify multi-channel audio is converted to 1D mono."""
        stereo = np.stack([self.clean_tone, self.clean_tone * 0.8], axis=0)  # shape (2, N)
        mono = to_mono(stereo)
        self.assertEqual(mono.ndim, 1)
        self.assertEqual(len(mono), len(self.clean_tone))

    def test_vad_preserves_speech_and_trims_silence(self):
        """Verify VAD trims leading/trailing silence without removing active speech."""
        silence_1s = np.zeros(int(self.sr * 1.0), dtype=np.float32)
        # Signal: 1s silence + 2s tone + 1s silence = 4s total
        padded_signal = np.concatenate([silence_1s, self.clean_tone, silence_1s])
        
        trimmed = trim_silence(padded_signal, sr=self.sr, top_db=30.0, pad_ms=100)
        
        # Trimmed length should be significantly less than 4s, but at least ~2s (the tone duration)
        self.assertGreater(len(trimmed), int(self.sr * 1.8), "VAD trimmed away active speech!")
        self.assertLess(len(trimmed), int(self.sr * 3.5), "VAD failed to trim surrounding silence!")

    def test_fold_local_normalization(self):
        """Verify fold-local normalization statistics (RC-08) are fitted and applied."""
        train_signals = [
            (0.2 * self.clean_tone),
            (0.4 * self.clean_tone)
        ]
        fold_stats = compute_fold_normalization_stats(train_signals, fold_id="fold_0")
        
        self.assertIn("ref_rms", fold_stats)
        self.assertIn("ref_peak", fold_stats)
        self.assertEqual(fold_stats["fitted_sample_count"], 2)
        
        # Test normalizing validation signal using training fold stats
        val_signal = 0.8 * self.clean_tone
        norm_val = normalize_loudness(val_signal, method="fold_stat", fold_stats=fold_stats)
        
        self.assertEqual(norm_val.ndim, 1)
        self.assertLessEqual(np.max(np.abs(norm_val)), 1.0)

    def test_unified_preprocess_pipeline(self):
        """Verify end-to-end preprocess_recording function."""
        result = preprocess_recording(self.clean_tone, orig_sr=self.sr)
        self.assertIn("audio", result)
        self.assertIn("sample_rate", result)
        self.assertIn("quality", result)
        self.assertTrue(result["is_acceptable"])
        self.assertEqual(result["sample_rate"], 16000)
        self.assertAlmostEqual(np.max(np.abs(result["audio"])), 0.95, delta=0.05)


if __name__ == "__main__":
    unittest.main()
