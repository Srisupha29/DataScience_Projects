import whisper

model = whisper.load_model("small")


def transcribe_audio(audio_file):
    """Convert an audio file into text using local Whisper."""

    audio_path = "temp_audio.wav"

    with open(audio_path, "wb") as f:
        f.write(audio_file.getbuffer())

    result = model.transcribe(audio_path)

    return result["text"]