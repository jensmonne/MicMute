import sounddevice as sd
import numpy as np
import keyboard  # New library for system-wide key presses
import time

# Parameters
AUDIO_DEVICE_NAME = "MicrophoneInput"  # Replace with your audio source name
SILENCE_DURATION = 10  # Seconds of silence before muting
CHECK_INTERVAL = 0.1  # How often to check audio levels

# Get the device ID for the audio source
def get_audio_device_id(device_name):
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device_name in device['name']:
            return idx
    raise ValueError(f"Audio device '{device_name}' not found!")

# Check if audio input is completely silent
def is_audio_active(device_id, duration=CHECK_INTERVAL):
    try:
        # Record a short audio sample
        audio_data = sd.rec(
            int(sd.query_devices(device_id, 'input')['default_samplerate'] * duration),
            samplerate=int(sd.query_devices(device_id, 'input')['default_samplerate']),
            channels=1,  # Single-channel (mono)
            device=device_id,
            dtype='float32'
        )
        sd.wait()  # Wait for the recording to complete
        return np.any(np.abs(audio_data) > 0.01)  # Check if any value is above absolute silence
    except Exception as e:
        print(f"Error accessing audio source: {e}")
        return True  # Fail-safe: Assume active if error occurs

# Simulate Discord mute toggle
def toggle_mute():
    keyboard.press_and_release('ctrl+shift+m')  # Simulate keypress for mute/unmute

# Main logic
def main():
    device_id = get_audio_device_id(AUDIO_DEVICE_NAME)
    silence_start = None

    print(f"Monitoring audio from: {AUDIO_DEVICE_NAME}")
    while True:
        audio_active = is_audio_active(device_id)
        if not audio_active:  # Mic is silent
            if silence_start is None:
                silence_start = time.time()
                print("Silence detected, starting timer...")
            elif time.time() - silence_start > SILENCE_DURATION:
                print("10 seconds of silence detected. Muting Discord...")
                toggle_mute()
                silence_start = None  # Reset after muting
        else:
            if silence_start is not None:
                print("Audio detected. Resetting silence timer...")
                silence_start = None  # Reset the timer if sound is detected
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()