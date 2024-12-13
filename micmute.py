import sounddevice as sd
import numpy as np
import pyautogui
import time

# Parameters
AUDIO_DEVICE_NAME = "HeadphonesMain"  # Replace with your audio source name
SILENCE_THRESHOLD = 0.01  # Adjust based on your noise level
SILENCE_DURATION = 3  # Seconds of silence before muting
CHECK_INTERVAL = 0.1  # How often to check audio levels

# Get the device ID for the audio source
def get_audio_device_id(device_name):
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device_name in device['name']:
            return idx
    raise ValueError(f"Audio device '{device_name}' not found!")

# Monitor audio levels
def is_audio_active(device_id):
    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        volume_norm = np.linalg.norm(indata) * 10
        return volume_norm > SILENCE_THRESHOLD

    try:
        with sd.InputStream(device=device_id, callback=audio_callback):
            audio_data = np.zeros((44100, 2))
            return np.linalg.norm(audio_data) > SILENCE_THRESHOLD
    except Exception as e:
        print(f"Error accessing audio source: {e}")
        return False

# Simulate Discord mute toggle
def toggle_mute():
    pyautogui.hotkey('ctrl', 'shift', 'm')  # Default Discord mute/unmute hotkey

# Main logic
def main():
    device_id = get_audio_device_id(AUDIO_DEVICE_NAME)
    silence_start = None

    print(f"Monitoring audio from: {AUDIO_DEVICE_NAME}")
    while True:
        audio_active = is_audio_active(device_id)
        if not audio_active:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start > SILENCE_DURATION:
                print("No audio detected. Muting Discord...")
                toggle_mute()
                silence_start = None  # Reset after muting
        else:
            if silence_start is not None:
                print("Audio detected. Unmuting Discord...")
                toggle_mute()
                silence_start = None
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()