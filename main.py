from flask import Flask, render_template, request, send_file
import edge_tts
import io
import os
from pydub import AudioSegment
import tempfile
import asyncio

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
            "km": "Khmer",
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
        return wav_stream
    except Exception as e:
        print(f"Error: {e}")
        return None

# ترجمات الجملة لجميع اللغات
translations = {
    "ar": "إذا أعجبتك الخدمة قم بالتبرع لدعم استمرار الموقع",
    "kn": "ನೀವು ಸೇವೆಯನ್ನು ಇಷ್ಟಪಡಿಸಿದರೆ, ದಯವಿಟ್ಟು ತಾಣವನ್ನು ಬೆಂಬಲಿಸಲು ದಾನ ಮಾಡಿ",
    "km": "ប្រសិនបើអ្នកចូលចិត្តសេវាកម្មនេះសូមឧបត្ថម្ភដើម្បីគាំទ្រទំព័រនេះ"
    # أضف المزيد من الترجمات هنا
}

@app.route("/", methods=["GET", "POST"])
def home():
    voices_data = asyncio.run(get_voice_list_async())
    if request.method == "POST":
        text = request.form["text"]
        voice = request.form["voice"]
        wav_stream = generate_audio(text, voice)
        if wav_stream is None:
            return "Error generating audio."
        return send_file(wav_stream, mimetype="audio/wav", as_attachment=True, download_name="output.wav")

    return render_template("index.html", voices_data=voices_data)

@app.route("/generate-audio", methods=["GET"])
def generate_audio_route():
    language = request.args.get("language")
    voice = request.args.get("voice")
    text = translations.get(language, translations["en"])  # النص المترجم

    wav_stream = generate_audio(text, voice)
    if wav_stream is None:
        return "Error generating audio."
    return send_file(wav_stream, mimetype="audio/wav")  # إرجاع الصوت للتشغيل في المتصفح

# مسارات الصفحات الإضافية
@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route("/about-us")
def about_us():
    return render_template("about_us.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
