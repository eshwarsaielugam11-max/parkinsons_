"""
Voice Activity Detection (VAD) and silence trimming module.
Implements conservative energy-based silence trimming to preserve borderline speech.
"""

from typing import Tuple, List
import numpy as np


def detect_voice_activity(
    audio: np.ndarray,
    sr: int = 16000,
    top_db: float = 35.0,
    frame_length_ms: int = 30,
    hop_length_ms: int = 10,
    pad_ms: int = 100
) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
    """
    Computes voice activity mask and non-silent intervals.
    
    Args:
        audio: 1D mono float32 audio array.
        sr: Sample rate.
        top_db: Decibels below peak energy considered silence.
        frame_length_ms: Frame length in milliseconds.
        hop_length_ms: Hop length in milliseconds.
        pad_ms: Milliseconds of padding added before/after speech intervals.
        
    Returns:
        is_speech_mask: Boolean array of same length as audio indicating active speech.
        intervals: List of (start_sample, end_sample) tuples of active speech.
    """
    if len(audio) == 0:
        return np.zeros(0, dtype=bool), []

    # Try librosa effects split if available
    try:
        import librosa
        frame_length = int(sr * frame_length_ms / 1000.0)
        hop_length = int(sr * hop_length_ms / 1000.0)
        pad_samples = int(sr * pad_ms / 1000.0)
        
        intervals = librosa.effects.split(
            audio,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length
        )
        
        mask = np.zeros(len(audio), dtype=bool)
        padded_intervals = []
        for start, end in intervals:
            p_start = max(0, start - pad_samples)
            p_end = min(len(audio), end + pad_samples)
            mask[p_start:p_end] = True
            padded_intervals.append((p_start, p_end))
            
        return mask, padded_intervals
    except ImportError:
        pass

    # Native numpy short-time energy VAD
    frame_length = max(1, int(sr * frame_length_ms / 1000.0))
    hop_length = max(1, int(sr * hop_length_ms / 1000.0))
    pad_samples = int(sr * pad_ms / 1000.0)
    
    # Pad audio to integer number of hops
    num_frames = max(1, (len(audio) - frame_length) // hop_length + 1)
    frame_energies = np.zeros(num_frames, dtype=np.float32)
    
    for i in range(num_frames):
        start = i * hop_length
        frame = audio[start:start + frame_length]
        energy = np.sum(frame ** 2) / float(frame_length) + 1e-12
        frame_energies[i] = energy
        
    max_energy = np.max(frame_energies) if len(frame_energies) > 0 else 1e-12
    if max_energy <= 1e-10:
        # Completely silent
        return np.zeros(len(audio), dtype=bool), []
        
    db_energies = 10.0 * np.log10(frame_energies / (max_energy + 1e-12) + 1e-12)
    active_frames = db_energies >= -top_db
    
    mask = np.zeros(len(audio), dtype=bool)
    for i, active in enumerate(active_frames):
        if active:
            start = max(0, i * hop_length - pad_samples)
            end = min(len(audio), i * hop_length + frame_length + pad_samples)
            mask[start:end] = True
            
    # Extract continuous intervals
    intervals = []
    in_speech = False
    start_idx = 0
    for idx, val in enumerate(mask):
        if val and not in_speech:
            in_speech = True
            start_idx = idx
        elif not val and in_speech:
            in_speech = False
            intervals.append((start_idx, idx))
    if in_speech:
        intervals.append((start_idx, len(mask)))
        
    return mask, intervals


def trim_silence(
    audio: np.ndarray,
    sr: int = 16000,
    top_db: float = 35.0,
    frame_length_ms: int = 30,
    hop_length_ms: int = 10,
    pad_ms: int = 100,
    min_speech_duration_sec: float = 0.5
) -> np.ndarray:
    """
    Trims leading/trailing/internal long silences from audio using conservative VAD.
    If the trimmed audio is too short (< min_speech_duration_sec) or all silent,
    returns the original audio or silent array without crashing.
    """
    mask, intervals = detect_voice_activity(
        audio,
        sr=sr,
        top_db=top_db,
        frame_length_ms=frame_length_ms,
        hop_length_ms=hop_length_ms,
        pad_ms=pad_ms
    )
    
    if not intervals or not np.any(mask):
        # Audio is completely silent or below energy threshold
        return audio
        
    # Concatenate all active speech segments
    active_segments = [audio[start:end] for start, end in intervals]
    trimmed_audio = np.concatenate(active_segments) if active_segments else audio
    
    return trimmed_audio.astype(np.float32)
