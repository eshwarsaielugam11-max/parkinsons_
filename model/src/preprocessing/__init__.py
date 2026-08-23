"""
Audio Preprocessing Package.
Exposes standardized modules for resampling, VAD, QA scoring, normalization, and unified pipeline.
"""

from .resample import resample_audio, to_mono
from .vad import detect_voice_activity, trim_silence
from .quality_check import compute_clipping_ratio, estimate_snr_db, compute_quality_score
from .normalize import normalize_loudness, compute_fold_normalization_stats
from .pipeline import preprocess_recording, load_audio_file

__all__ = [
    "preprocess_recording",
    "load_audio_file",
    "resample_audio",
    "to_mono",
    "detect_voice_activity",
    "trim_silence",
    "compute_clipping_ratio",
    "estimate_snr_db",
    "compute_quality_score",
    "normalize_loudness",
    "compute_fold_normalization_stats"
]
