"""
Tone Generator for Frequency Sampler Test

Test sequence per target frequency:
1. Target frequency for 5 seconds
2. Target - 100 Hz for 5 seconds
3. Target frequency for 5 seconds
4. Target + 100 Hz for 5 seconds
5. Target frequency for 5 seconds

Total: 25 seconds per frequency
Target frequencies: 500 Hz, 800 Hz, 1 kHz, 10 kHz
"""

import numpy as np
import sounddevice as sd
import time

# -----------------------
# Configuration
# -----------------------
SAMPLE_RATE = 44100  # Standard audio sample rate
AMPLITUDE = 0.5      # Volume (0.0 to 1.0)
SEGMENT_DURATION = 5  # seconds per segment
FREQ_OFFSET = 100    # Hz offset for deviation

TARGET_FREQUENCIES = [500, 800, 1000, 10000]  # Hz


def generate_tone(frequency: float, duration: float, sample_rate: int = SAMPLE_RATE, amplitude: float = AMPLITUDE) -> np.ndarray:
    """Generate a sinusoidal tone at the specified frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = amplitude * np.sin(2 * np.pi * frequency * t)
    return tone.astype(np.float32)


def play_tone(frequency: float, duration: float, label: str = ""):
    """Play a tone at the specified frequency for the given duration."""
    print(f"  Playing {frequency} Hz ({label})...", end=" ", flush=True)
    tone = generate_tone(frequency, duration)
    sd.play(tone, samplerate=SAMPLE_RATE)
    sd.wait()
    print("done")


def run_test_sequence(target_freq: float):
    """
    Run the test sequence for a single target frequency:
    1. Target for 5s
    2. Target - 100 Hz for 5s
    3. Target for 5s
    4. Target + 100 Hz for 5s
    5. Target for 5s
    """
    print(f"\n{'='*50}")
    print(f"Starting test for target frequency: {target_freq} Hz")
    print(f"{'='*50}")
    
    # Calculate frequencies
    freq_low = target_freq - FREQ_OFFSET
    freq_high = target_freq + FREQ_OFFSET
    
    print(f"  Sequence: {target_freq} → {freq_low} → {target_freq} → {freq_high} → {target_freq}")
    print(f"  Total duration: {SEGMENT_DURATION * 5} seconds")
    print()
    
    # Sequence
    play_tone(target_freq, SEGMENT_DURATION, "target")
    play_tone(freq_low, SEGMENT_DURATION, f"target - {FREQ_OFFSET}")
    play_tone(target_freq, SEGMENT_DURATION, "target")
    play_tone(freq_high, SEGMENT_DURATION, f"target + {FREQ_OFFSET}")
    play_tone(target_freq, SEGMENT_DURATION, "target")
    
    print(f"Test for {target_freq} Hz complete!")


def run_single_test(target_freq: float):
    """Run test for a single target frequency."""
    print("\n" + "="*60)
    print(f"SINGLE TEST MODE: {target_freq} Hz")
    print("="*60)
    
    input(f"\nPress Enter to start test for {target_freq} Hz...")
    run_test_sequence(target_freq)
    print("\n✓ Test complete!")


def run_all_tests():
    """Run tests for all target frequencies with pauses between."""
    print("\n" + "="*60)
    print("FULL TEST SEQUENCE")
    print(f"Frequencies: {TARGET_FREQUENCIES}")
    print(f"Duration per frequency: {SEGMENT_DURATION * 5} seconds")
    print(f"Total estimated time: {SEGMENT_DURATION * 5 * len(TARGET_FREQUENCIES)} seconds")
    print("="*60)
    
    for i, freq in enumerate(TARGET_FREQUENCIES, 1):
        input(f"\nPress Enter to start test {i}/{len(TARGET_FREQUENCIES)} ({freq} Hz)...")
        run_test_sequence(freq)
        print(f"\n--- Completed {i}/{len(TARGET_FREQUENCIES)} tests ---")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)


def continuous_mode(target_freq: float):
    """
    Continuous mode: Play the test sequence on loop until stopped.
    Useful for debugging or calibration.
    """
    print("\n" + "="*60)
    print(f"CONTINUOUS MODE: {target_freq} Hz")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    try:
        iteration = 1
        while True:
            print(f"\n--- Iteration {iteration} ---")
            run_test_sequence(target_freq)
            iteration += 1
    except KeyboardInterrupt:
        print("\n\nStopped by user.")


def main():
    """Main entry point with menu."""
    print("\n" + "="*60)
    print("FREQUENCY SAMPLER TONE GENERATOR")
    print("="*60)
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    print(f"\nDefault output device: {sd.query_devices(kind='output')['name']}")
    
    while True:
        print("\n" + "-"*40)
        print("Options:")
        print("  1. Run all tests (500, 800, 1000, 10000 Hz)")
        print("  2. Run single test")
        print("  3. Continuous mode (loop single frequency)")
        print("  4. Quick test (1 second beep)")
        print("  5. Exit")
        print("-"*40)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            run_all_tests()
        
        elif choice == "2":
            print(f"\nAvailable frequencies: {TARGET_FREQUENCIES}")
            freq_str = input("Enter target frequency (Hz): ").strip()
            try:
                freq = float(freq_str)
                run_single_test(freq)
            except ValueError:
                print("Invalid frequency. Please enter a number.")
        
        elif choice == "3":
            print(f"\nAvailable frequencies: {TARGET_FREQUENCIES}")
            freq_str = input("Enter target frequency (Hz): ").strip()
            try:
                freq = float(freq_str)
                continuous_mode(freq)
            except ValueError:
                print("Invalid frequency. Please enter a number.")
        
        elif choice == "4":
            print("\nPlaying 1 second test tone at 440 Hz...")
            play_tone(440, 1.0, "test beep")
            print("Done!")
        
        elif choice == "5":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-5.")


if __name__ == "__main__":
    main()
