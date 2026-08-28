import os
import math
import wave
import struct
import subprocess


STARTUP_FILE = os.path.join(
    os.path.dirname(__file__),
    "startup.wav"
)


def create_startup_sound():
    """Create a short futuristic electronic startup sound."""

    sample_rate = 44100
    duration = 1.5

    samples = []

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate

        # Main rising frequency
        frequency = 180 + (900 * t / duration)

        # Electronic tones
        tone = (
            0.35 * math.sin(2 * math.pi * frequency * t)
            + 0.18 * math.sin(2 * math.pi * frequency * 2 * t)
            + 0.08 * math.sin(2 * math.pi * 70 * t)
        )

        # Fade in/out
        fade_in = min(1.0, t / 0.15)
        fade_out = min(1.0, (duration - t) / 0.35)

        volume = fade_in * fade_out

        value = int(
            max(-1, min(1, tone * volume)) * 32767
        )

        samples.append(
            struct.pack("<h", value)
        )

    with wave.open(STARTUP_FILE, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"".join(samples))


def startup_sound():
    """Play the ULTRON startup sound."""

    if not os.path.exists(STARTUP_FILE):
        create_startup_sound()
    try:
        import winsound
        # Ensure any previous sounds are stopped, then play async
        winsound.PlaySound(None, winsound.SND_PURGE)
        winsound.PlaySound(
            STARTUP_FILE,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
        print("[VOICE] Startup sound played (async).")
    except ImportError:
        print("[VOICE] Startup sound skipped (winsound not available on this platform).")
    except Exception as e:
        print("[VOICE] Failed to play startup sound:", e)
def shutdown_sound():
    """Play the ULTRON shutdown sound."""

    sample_rate = 44100
    duration = 1.5
    samples = []

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate

        # Falling futuristic tone
        frequency = 900 - (700 * t / duration)

        tone = (
            0.35 * math.sin(2 * math.pi * frequency * t)
            + 0.15 * math.sin(2 * math.pi * frequency * 2 * t)
            + 0.06 * math.sin(2 * math.pi * 60 * t)
        )

        fade_in = min(1.0, t / 0.08)
        fade_out = min(1.0, (duration - t) / 0.3)

        volume = fade_in * fade_out

        value = int(
            max(-1, min(1, tone * volume)) * 32767
        )

        samples.append(struct.pack("<h", value))

    shutdown_file = os.path.join(
        os.path.dirname(__file__),
        "shutdown.wav"
    )

    with wave.open(shutdown_file, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(b"".join(samples))

    try:
        import winsound
        winsound.PlaySound(None, winsound.SND_PURGE)
        winsound.PlaySound(
            shutdown_file,
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
        print("[VOICE] Shutdown sound played (async).")
    except ImportError:
        print("[VOICE] Shutdown sound skipped (winsound not available on this platform).")
    except Exception as e:
        print("[VOICE] Failed to play shutdown sound:", e)

def windows_voice(text):
    """Fallback Windows voice."""

    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$speak.Rate = -1; "
        "$speak.Volume = 100; "
        f'$speak.Speak("{text}")'
    )

    subprocess.run(
        ["powershell", "-Command", command],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def speak(text):
    """
    ULTRON voice interface.

    Currently uses Windows TTS.
    Later this function can use a neural local voice such as Piper.
    """

    windows_voice(text)


def startup():
    """Complete ULTRON startup sequence."""

    print("[VOICE] Initializing...")

    startup_sound()

    print("[VOICE] ULTRON voice online.")

    speak("Ultron online,boss.")



def shutdown():
    """Complete ULTRON shutdown sequence."""

    print("[VOICE] Shutting down...")

    try:
        shutdown_sound()
    except Exception as e:
        print("[VOICE] Failed to play shutdown sound:", e)

    try:
        speak("Ultron shutting down,boss.")
    except Exception as e:
        print("[VOICE] TTS failed:", e)

    print("[VOICE] ULTRON offline.")


if __name__ == "__main__":
    startup()