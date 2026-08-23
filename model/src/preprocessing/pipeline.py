"""
Unified Audio Preprocessing Pipeline.
Shared across training pipelines, notebooks, and production backend services.
"""

from typing import Union, Dict, Any, Optional, Tuple
from pathlib import Path
import os
import wave
import struct
import numpy as np

from .resample import resample_audio, to_mono
from .vad import trim_silence, detect_voice_activity
from .quality_check import compute_quality_score, compute_clipping_ratio, estimate_snr_db
from .normalize import normalize_loudness, compute_fold_normalization_stats


def load_audio_file(file_path: Union[str, Path]) -> Tuple[np.ndarray, int]:
    """
    Loads audio file into float32 numpy array and sample rate.
    Uses soundfile/librosa if available, with standard library wave fallback.
    """
    path_str = str(file_path)
    
    # Try soundfile
    try:
        import soundfile as sf
        audio, sr = sf.read(path_str, dtype="float32")
        return audio, sr
    except (ImportError, Exception):
        pass

    # Try librosa
    try:
        import librosa
        audio, sr = librosa.load(path_str, sr=None, mono=False)
        return audio.astype(np.float32), sr
    except (ImportError, Exception):
        pass

    # Fallback to standard library wave
    try:
        with wave.open(path_str, "rb") as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)
            
            if sampwidth == 2:  # 16-bit PCM
                count = n_frames * n_channels
                shorts = struct.unpack(f"<{count}h", raw_data)
                audio = np.array(shorts, dtype=np.float32) / 32768.0
            elif sampwidth == 4:  # 32-bit float or int
                count = n_frames * n_channels
                floats = struct.unpack(f"<{count}f", raw_data)
                audio = np.array(floats, dtype=np.float32)
            else:
                count = n_frames * n_channels
                audio = np.frombuffer(raw_data, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
                
            if n_channels > 1:
                audio = audio.reshape(-1, n_channels).T
            return audio, framerate
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file {path_str}: {e}")


def preprocess_recording(
    audio_input: Union[str, Path, np.ndarray],
    orig_sr: Optional[int] = None,
    config: Optional[Dict[str, Any]] = None,
    fold_stats: Optional[Dict[str, Any]] = None,
    trim_silence_flag: bool = True
) -> Dict[str, Any]:
    """
    Standardized preprocessing function used identically in training and deployment.
    
    Processing Steps:
      1. Load audio (if file path) & convert to mono
      2. Resample to target sample rate (default: 16000 Hz)
      3. Quality evaluation & rejection scoring (Constraint RC-11/RC-12)
      4. Conservative Voice Activity Detection (VAD) & silence trimming (Constraint RC-05)
      5. Loudness normalization (peak / fold-local reference level per Constraint RC-08)
      
    Args:
        audio_input: File path or raw 1D/2D audio numpy array.
        orig_sr: Original sample rate (required if audio_input is numpy array).
        config: Preprocessing config dictionary (or default fallback).
        fold_stats: Optional fold-fitted normalization statistics (Constraint RC-08).
        trim_silence_flag: Whether to perform conservative VAD silence trimming.
        
    Returns:
        Dict containing:
          - "audio": 1D np.ndarray (float32, normalized, trimmed)
          - "sample_rate": int target sample rate
          - "quality": Dict quality metrics & acceptance status
          - "is_acceptable": bool
          - "preprocessed": bool
          - "fold_stats_applied": bool
    """
    if config is None:
        config = {
            "target_sample_rate": 16000,
            "vad": {
                "top_db": 35.0,
                "frame_length_ms": 30,
                "hop_length_ms": 10,
                "pad_ms": 100,
                "min_valid_speech_seconds": 0.5
            },
            "quality": {
                "clipping_threshold": 0.999,
                "max_clipping_ratio": 0.005,
                "min_snr_db": 8.0,
                "min_duration_seconds": 0.8,
                "min_quality_score": 0.60
            },
            "normalization": {
                "method": "peak",
                "target_peak_level": 0.95,
                "target_rms_level": 0.10
            }
        }
        
    target_sr = config.get("target_sample_rate", 16000)
    
    # 1. Ingest input
    if isinstance(audio_input, (str, Path)):
        raw_audio, in_sr = load_audio_file(audio_input)
    elif isinstance(audio_input, np.ndarray):
        raw_audio = audio_input
        in_sr = orig_sr if orig_sr is not None else target_sr
    else:
        raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
        
    # Convert to mono
    mono_audio = to_mono(raw_audio)
    
    # 2. Resample to target sample rate
    resampled_audio, out_sr = resample_audio(mono_audio, orig_sr=in_sr, target_sr=target_sr)
    
    # 3. Quality evaluation before modification
    quality_result = compute_quality_score(resampled_audio, sr=out_sr, config=config)
    
    # 4. Conservative VAD & Silence Trimming
    vad_cfg = config.get("vad", {})
    if trim_silence_flag and len(resampled_audio) > 0:
        processed_audio = trim_silence(
            resampled_audio,
            sr=out_sr,
            top_db=vad_cfg.get("top_db", 35.0),
            frame_length_ms=vad_cfg.get("frame_length_ms", 30),
            hop_length_ms=vad_cfg.get("hop_length_ms", 10),
            pad_ms=vad_cfg.get("pad_ms", 100),
            min_speech_duration_sec=vad_cfg.get("min_valid_speech_seconds", 0.5)
        )
    else:
        processed_audio = resampled_audio
        
    # 5. Loudness Normalization (Fold-Local Aware)
    norm_cfg = config.get("normalization", {})
    norm_method = "fold_stat" if fold_stats is not None else norm_cfg.get("method", "peak")
    
    normalized_audio = normalize_loudness(
        processed_audio,
        method=norm_method,
        target_peak=norm_cfg.get("target_peak_level", 0.95),
        target_rms=norm_cfg.get("target_rms_level", 0.10),
        fold_stats=fold_stats
    )
    
    return {
        "audio": normalized_audio,
        "sample_rate": out_sr,
        "quality": quality_result,
        "is_acceptable": quality_result.get("is_acceptable", False),
        "preprocessed": True,
        "fold_stats_applied": bool(fold_stats is not None),
        "duration_sec": round(len(normalized_audio) / float(out_sr), 3) if out_sr else 0.0
    }
