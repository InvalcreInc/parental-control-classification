import speech_recognition as sr
from io import BytesIO
from requests import get
from pydub import AudioSegment


def transcribe_audio(url, max_tokens=1000, duration=2) -> str | None:
    try:
        audio_data = download_audio(url)
        r = sr.Recognizer()
        audio_file = sr.AudioFile(audio_data)
        with audio_file as source:
            r.adjust_for_ambient_noise()
            audio = r.record(source, duration=duration)
        text = sr.recognize_google(audio)
        return text[:max_tokens]
    except Exception as e:
        print(e)
        return None


def download_audio(url):
    res = get(url)
    if res.status_code != 200:
        raise Exception(f"Error: {res.status_code}")
    audio_data = BytesIO(res.content)
    audio_file = AudioSegment.from_file(audio_data)
    wav_file_path = "temp.wav"
    audio_file.export(wav_file_path, format="wav")
    return wav_file_path


if __name__ == "__main__":
    print(transcribe_audio(
        "https://dn721901.ca.archive.org/0/items/anthonybenezet_2505_librivox/anthonybenezet_00_vaux_128kb.mp3"))
