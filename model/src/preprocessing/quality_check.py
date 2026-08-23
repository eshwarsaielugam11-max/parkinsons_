"""
Audio Quality Assurance & Objective Scoring Module.
Computes clipping, estimated SNR, duration, and composite audio quality score in [0, 1].
"""

from typing import Dict, Any, List
import numpy as np


def compute_clipping_ratio(
    audio: np.ndarray,
    threshold: float = 0.999
) -> float:
    """
    Computes the fraction of audio samples that exceed or meet the saturation threshold.
    """
    if len(audio) == 0:
        return 0.0
    abs_audio = np.abs(audio)
    clipped_samples = np.sum(abs_audio >= threshold)
    return float(clipped_samples / len(audio))


def estimate_snr_db(
    audio: np.ndarray,
    sr: int = 16000,
    top_db: float = 35.0
) -> float:
    """
    Estimates Signal-to-Noise Ratio (SNR) in dB.
    Handles conversational speech (with pause segments) and sustained phonations/tones.
    """
    if len(audio) == 0:
        return 0.0
        
    abs_audio = np.abs(audio)
    peak = np.max(abs_audio)
    if peak <= 1e-6:
        return 0.0
        
    # Total signal RMS power
    total_power = np.mean(audio ** 2) + 1e-12
    
    # Frame-level RMS energy
    frame_len = max(1, int(sr * 0.03))
    hop_len = max(1, int(sr * 0.01))
    num_frames = max(1, (len(audio) - frame_len) // hop_len + 1)
    
    energies = np.zeros(num_frames, dtype=np.float32)
    for i in range(num_frames):
        st = i * hop_len
        energies[i] = np.mean(audio[st:st + frame_len] ** 2)
        
    max_frame_e = np.max(energies)
    min_frame_e = np.min(energies)
    
    # If there is energy dynamic range (speech with pauses/background noise)
    if min_frame_e < 0.15 * max_frame_e:
        sorted_energies = np.sort(energies)
        noise_idx = max(1, int(0.15 * num_frames))
        noise_power = np.mean(sorted_energies[:noise_idx]) + 1e-12
        signal_idx = max(1, int(0.60 * num_frames))
        signal_power = np.mean(sorted_energies[signal_idx:]) + 1e-12
        snr = 10.0 * np.log10(signal_power / noise_power)
    else:
        # Continuous tone or sustained vowel: estimate noise floor via high-frequency derivative/residual
        # First-difference acts as high-pass residual filter
        diff_signal = np.diff(audio)
        noise_floor_est = max(1e-10, np.var(diff_signal) * 0.1)
        snr = 10.0 * np.log10(total_power / noise_floor_est)
        # Cap for clean tone
        snr = max(20.0, min(50.0, snr))
        
    return float(max(0.0, min(60.0, snr)))


def compute_quality_score(
    audio: np.ndarray,
    sr: int = 16000,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Evaluates audio signal against QA thresholds and returns a composite quality score in [0, 1].
    
    Returns dictionary with:
      - audio_quality_score: float in [0.0, 1.0]
      - is_acceptable: bool
      - clipping_ratio: float
      - estimated_snr_db: float
      - duration_sec: float
      - rejection_reasons: list[str]
    """
    cfg = config.get("quality", {}) if config else {}
    clipping_thresh = cfg.get("clipping_threshold", 0.999)
    max_clipping_ratio = cfg.get("max_clipping_ratio", 0.005)
    min_snr_db = cfg.get("min_snr_db", 8.0)
    min_duration = cfg.get("min_duration_seconds", 0.8)
    min_score = cfg.get("min_quality_score", 0.60)
    
    duration = len(audio) / max(1, sr) if len(audio) > 0 else 0.0
    clipping_ratio = compute_clipping_ratio(audio, threshold=clipping_thresh)
    snr_db = estimate_snr_db(audio, sr=sr)
    
    rejection_reasons = []
    
    # Check silent or empty
    if len(audio) == 0 or np.max(np.abs(audio)) < 1e-5:
        rejection_reasons.append("SILENT_OR_EMPTY_AUDIO")
        return {
            "audio_quality_score": 0.0,
            "is_acceptable": False,
            "clipping_ratio": 0.0,
            "estimated_snr_db": 0.0,
            "duration_sec": duration,
            "rejection_reasons": rejection_reasons
        }
        
    # Check clipping
    if clipping_ratio > max_clipping_ratio:
        rejection_reasons.append(f"HIGH_CLIPPING (ratio={clipping_ratio:.4f} > {max_clipping_ratio})")
        
    # Check SNR
    if snr_db < min_snr_db:
        rejection_reasons.append(f"LOW_SNR (snr={snr_db:.1f}dB < {min_snr_db}dB)")
        
    # Check Duration
    if duration < min_duration:
        rejection_reasons.append(f"INSUFFICIENT_DURATION ({duration:.2f}s < {min_duration}s)")
        
    # Compute composite continuous score in [0.0, 1.0]
    # SNR sub-score: maps [0, 30 dB] -> [0.0, 1.0]
    snr_subscore = min(1.0, snr_db / 30.0)
    # Clipping sub-score: 1.0 for 0 clipping, dropping to 0 at 2% clipping
    clip_subscore = max(0.0, 1.0 - (clipping_ratio / 0.02))
    # Duration sub-score: 1.0 for >= 2s, ramping linearly from 0.8s
    dur_subscore = min(1.0, max(0.0, (duration - 0.5) / 1.5))
    
    composite_score = float(0.50 * snr_subscore + 0.30 * clip_subscore + 0.20 * dur_subscore)
    composite_score = round(max(0.0, min(1.0, composite_score)), 4)
    
    is_acceptable = (composite_score >= min_score) and (len(rejection_reasons) == 0)
    
    return {
        "audio_quality_score": composite_score,
        "is_acceptable": is_acceptable,
        "clipping_ratio": float(clipping_ratio),
        "estimated_snr_db": float(snr_db),
        "duration_sec": float(round(duration, 3)),
        "rejection_reasons": rejection_reasons
    }
