# Real-Time Frequency Sampler

A frequency magnitude monitor for Raspberry Pi using the Goertzel algorithm, with a companion tone generator for PC-based testing.

## Overview

This project consists of two components:

1. **`pi.py`** - Raspberry Pi script that monitors audio input for a specific frequency and displays magnitude via web UI
2. **`tone_generator.py`** - PC utility that generates test tones to validate the Pi's frequency detection

## Components

### Raspberry Pi Script (`pi.py`)

A Flask-based web application that:
- Captures audio input using sounddevice
- Computes magnitude at a target frequency using the Goertzel algorithm
- Serves a web UI on port 5000 for real-time monitoring
- Supports logging magnitude data to CSV

**Features:**
- Real-time magnitude display (updates every 25ms)
- Adjustable target frequency via web UI
- Start/stop CSV logging with timestamps
- Thread-safe audio processing

### Tone Generator (`tone_generator.py`)

A PC utility for testing the Raspberry Pi's frequency detection:

**Test Sequence (per target frequency):**
1. Target frequency for 5 seconds
2. Target - 100 Hz for 5 seconds
3. Target frequency for 5 seconds
4. Target + 100 Hz for 5 seconds
5. Target frequency for 5 seconds

**Modes:**
- **All tests**: Run sequence for 500, 800, 1000, 10000 Hz
- **Single test**: Run sequence for a specific frequency
- **Continuous mode**: Loop the sequence for calibration/debugging
- **Quick test**: 1-second beep at 440 Hz

## Requirements

- Python 3.13+
- PortAudio library (for sounddevice)

### Dependencies

```
flask>=3.1.2
numpy>=2.4.1
sounddevice>=0.5.5
```

### Installing PortAudio

| Platform | Command |
|----------|---------|
| macOS | `brew install portaudio` |
| Ubuntu/Debian | `sudo apt-get install portaudio19-dev` |
| Raspberry Pi OS | `sudo apt-get install portaudio19-dev` |
| Windows | Bundled with sounddevice |

## Setup

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Run Pi script
uv run pi.py

# Run tone generator
uv run tone_generator.py
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask numpy sounddevice

# Run Pi script
python pi.py

# Run tone generator
python tone_generator.py
```

## Usage

### On Raspberry Pi

1. Connect an audio input device (microphone or line-in)
2. Run the frequency monitor:
   ```bash
   python pi.py
   ```
3. Access the web UI at `http://<pi-ip-address>:5000`
4. Set the target frequency you want to monitor
5. Optionally enable logging to save magnitude data to `frequency_log.csv`

### On PC (for testing)

1. Connect audio output to the Pi's audio input (or use speakers near Pi's microphone)
2. Run the tone generator:
   ```bash
   python tone_generator.py
   ```
3. Select a test mode from the menu
4. Observe the magnitude readings on the Pi's web UI

### Test Workflow

1. Start `pi.py` on the Raspberry Pi
2. Open the Pi's web UI in a browser
3. Set the target frequency (e.g., 1000 Hz)
4. On PC, run `tone_generator.py` and select "Run single test" with 1000 Hz
5. Watch the magnitude on the Pi:
   - Should be high during target frequency segments
   - Should drop during ±100 Hz deviation segments

## Configuration

### Pi Script (`pi.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `FS` | 48000 | Sampling rate (Hz) |
| `N` | 1024 | Block size for Goertzel |
| `LOG_FILE` | `frequency_log.csv` | Output log file |
| `target_frequency` | 1000 | Initial target frequency (Hz) |

### Tone Generator (`tone_generator.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SAMPLE_RATE` | 44100 | Audio sample rate (Hz) |
| `AMPLITUDE` | 0.5 | Volume (0.0 to 1.0) |
| `SEGMENT_DURATION` | 5 | Seconds per segment |
| `FREQ_OFFSET` | 100 | Hz offset for deviation tests |
| `TARGET_FREQUENCIES` | [500, 800, 1000, 10000] | Preset frequencies |

## Output Files

- `frequency_log.csv` - Logged magnitude data with timestamps (when logging enabled on Pi)

## License

See LICENSE file.
