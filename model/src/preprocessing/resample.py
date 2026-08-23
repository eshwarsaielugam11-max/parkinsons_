"""
Audio resampling and channel standardization module.
"""

from typing import Tuple, Union
import numpy as np


def to_mono(audio: np.ndarray) -> np.ndarray:
    """
    Converts multi-channel audio array to mono by averaging across channels.
    Expected audio shape: (samples,) or (channels, samples) or (samples, channels).
    Returns shape: (samples,).
    """
    if audio.ndim == 1:
        return audio.astype(np.float32)
    
    if audio.ndim == 2:
        # If channels is the first dimension (e.g. (2, N))
        if audio.shape[0] < audio.shape[1]:
            return np.mean(audio, axis=0, dtype=np.float32)
        # If channels is the second dimension (e.g. (N, 2))
        else:
            return np.mean(audio, axis=1, dtype=np.float32)
            
    raise ValueError(f"Unsupported audio array dimension: {audio.ndim}")


def resample_audio(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int = 16000
) -> Tuple[np.ndarray, int]:
    """
    Resamples audio to target sample rate.
    Uses librosa/scipy if available, otherwise high-precision numpy interpolation.
    """
    if orig_sr == target_sr:
        return to_mono(audio), target_sr
        
    mono_audio = to_mono(audio)
    
    # Attempt librosa
    try:
        import librosa
        resampled = librosa.resample(mono_audio, orig_sr=orig_sr, target_sr=target_sr)
        return resampled.astype(np.float32), target_sr
    except ImportError:
        pass

    # Attempt scipy.signal.resample_poly
    try:
        from scipy.signal import resample_poly
        import math
        gcd = math.gcd(int(orig_sr), int(target_sr))
        up = target_sr // gcd
        down = orig_sr // gcd
        resampled = resample_poly(mono_audio, up, down)
        return resampled.astype(np.float32), target_sr
    except ImportError:
        pass

    # Fallback to high-quality linear interpolation in numpy
    duration = len(mono_audio) / orig_sr
    num_target_samples = int(round(duration * target_sr))
    orig_timestamps = np.linspace(0, duration, len(mono_audio), endpoint=False)
    target_timestamps = np.linspace(0, duration, num_target_samples, endpoint=False)
    resampled = np.interp(target_timestamps, orig_timestamps, mono_audio)
    return resampled.astype(np.float32), target_sr
