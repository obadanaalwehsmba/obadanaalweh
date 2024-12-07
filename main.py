from flask import Flask, render_template, request, send_file
import edge_tts
import io
import os
from pydub import AudioSegment
import tempfile
import asyncio
import requests  # لإرسال الملف إلى transfer.sh

app = Flask(__name__)

# دالة لجلب قائمة الأصوات باستخدام async
async def get_voice_list_async():
    voices = await edge_tts.list_voices()
    languages = {}

    # دالة لتحديد اسم اللغة بناءً على الـ Locale
    def get_language_name(locale):
        language_map = {
            "en": "English",
            "ar": "Arabic",
            # أضف المزيد من اللغات هنا عند الحاجة
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

# دالة لتحويل النص إلى صوت
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
        
        # رفع الملف إلى transfer.sh
        upload_url = upload_to_transfer_sh(wav_stream)
        if upload_url is None:
            return "Error uploading to transfer.sh"
        return upload_url
    except Exception as e:
        print(f"Error generating audio: {e}")
        return "Error generating audio."

# دالة لرفع الملف إلى transfer.sh
def upload_to_transfer_sh(file_stream):
    url = "https://transfer.sh/"
    file_stream.seek(0)
    response = requests.put(url + "output.wav", data=file_stream)
    
    if response.status_code == 200:
        return response.text  # الرابط المباشر للتحميل
    else:
        print(f"Failed to upload file. Status code: {response.status_code}")
        return None

# ترجمات الجملة لجميع اللغات
translations = {
    "ar": "إذا أعجبتك الخدمة قم بالتبرع لدعم استمرار الموقع",
    "en": "If you like the service, please donate to support the site",
    # أضف المزيد من الترجمات هنا
}

@app.route("/", methods=["GET", "POST"])
def home():
    voices_data = asyncio.run(get_voice_list_async())
    if request.method == "POST":
        text = request.form["text"]
        voice = request.form["voice"]
        file_url = generate_audio(text, voice)
        if file_url is None:
            return "Error generating audio."
        return f'<a href="{file_url}" download>Download your audio file</a>'  # الرابط لتحميل الملف

    return render_template("index.html", voices_data=voices_data)

@app.route("/generate-audio", methods=["GET"])
def generate_audio_route():
    language = request.args.get("language")
    voice = request.args.get("voice")
    text = translations.get(language, translations["en"])  # النص المترجم

    file_url = generate_audio(text, voice)
    if file_url is None:
        return "Error generating audio."
    return f'<a href="{file_url}" download>Download your audio file</a>'  # الرابط لتحميل الملف

if __name__ == "__main__":
    # استخدام البورت الذي يتم تحديده من البيئة
    port = os.getenv("PORT", 5000)  # استخدام البورت من المتغير أو 5000 إذا لم يكن موجود
    app.run(debug=True, host="0.0.0.0", port=int(port))
