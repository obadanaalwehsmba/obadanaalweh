from flask import Flask, render_template, request
import edge_tts
import asyncio
import requests
import tempfile
import os
from pydub import AudioSegment
import io

app = Flask(__name__)

# Helper function to get the voice list asynchronously
async def get_voice_list_async():
    voices = await edge_tts.list_voices()
    languages = {}

    def get_language_name(locale):
        language_map = {
            "en": "English",
            "ar": "Arabic",
            # Add more languages here as needed
        }
        return language_map.get(locale.split('-')[0], locale)

    for voice in voices:
        lang = voice["Locale"]
        name = voice["ShortName"]
        language_name = get_language_name(lang)
        if language_name not in languages:
            languages[language_name] = []
        languages[language_name].append(name)
    
    return languages

# Function to generate audio and upload to transfer.sh
def generate_audio(text, voice):
    try:
        tts = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            asyncio.run(tts.save(temp_file_name))
        
        audio = AudioSegment.from_file(temp_file_name)
        wav_stream = io.BytesIO()
        audio.export(wav_stream, format="wav")
        wav_stream.seek(0)
        os.remove(temp_file_name)

        # Upload to transfer.sh
        upload_url = upload_to_transfer_sh(wav_stream)
        return upload_url
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to upload file to transfer.sh
def upload_to_transfer_sh(file_stream):
    url = "https://transfer.sh/output.wav"
    file_stream.seek(0)
    response = requests.put(url, data=file_stream)
    if response.status_code == 200:
        return response.text  # Direct download link
    else:
        print("Failed to upload file.")
        return None

# Route to handle form submission and audio generation
@app.route("/", methods=["GET", "POST"])
def home():
    voices_data = asyncio.run(get_voice_list_async())
    file_url = None
    if request.method == "POST":
        text = request.form["text"]
        voice = request.form["voice"]
        file_url = generate_audio(text, voice)
        if file_url is None:
            return "Error generating audio."

    return render_template("index.html", voices_data=voices_data, file_url=file_url)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
