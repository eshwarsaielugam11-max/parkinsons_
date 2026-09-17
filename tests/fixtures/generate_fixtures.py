import os
import wave
import numpy as np

def generate_fixtures(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    sr = 16000
    duration = 3.0
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 1. Clean synthetic sustained phonation (/a/ vowel ~150Hz with natural harmonics)
    f0 = 150.0
    clean_audio = (
        0.5 * np.sin(2 * np.pi * f0 * t) +
        0.25 * np.sin(2 * np.pi * 2 * f0 * t) +
        0.15 * np.sin(2 * np.pi * 3 * f0 * t) +
        0.05 * np.random.normal(0, 0.01, num_samples)
    )
    clean_int16 = (clean_audio * 32767).astype(np.int16)
    with wave.open(os.path.join(output_dir, "clean_sample.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(clean_int16.tobytes())

    # 2. Noisy speech (heavy gaussian noise and low SNR)
    noisy_audio = 0.2 * np.sin(2 * np.pi * f0 * t) + 0.6 * np.random.normal(0, 0.4, num_samples)
    noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
    noisy_int16 = (noisy_audio * 32767).astype(np.int16)
    with wave.open(os.path.join(output_dir, "noisy_sample.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(noisy_int16.tobytes())

    # 3. Silent / low-energy rejected audio (near 0 signal)
    silent_audio = np.zeros(num_samples, dtype=np.float32)
    silent_int16 = (silent_audio * 32767).astype(np.int16)
    with wave.open(os.path.join(output_dir, "silent_rejected.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(silent_int16.tobytes())

if __name__ == "__main__":
    fixtures_dir = os.path.dirname(__file__)
    generate_fixtures(fixtures_dir)
    print(f"Generated fixture files in {fixtures_dir}")
