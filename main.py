from flask import Flask, render_template, request, send_file
import edge_tts
import io
import os
from pydub import AudioSegment
import tempfile
import asyncio
import os

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
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "pt": "Portuguese",
            "it": "Italian",
            "tr": "Turkish",
            "pl": "Polish",
            "nl": "Dutch",
            "sv": "Swedish",
            "fi": "Finnish",
            "no": "Norwegian",
            "da": "Danish",
            "hi": "Hindi",
            "id": "Indonesian",
            "vi": "Vietnamese",
            "th": "Thai",
            "ms": "Malay",
            "fa": "Persian",
            "uk": "Ukrainian",
            "ro": "Romanian",
            "sr": "Serbian",
            "bg": "Bulgarian",
            "az": "Azerbaijani",
            "my": "Burmese",
            "ca": "Catalan",
            "sq": "Albanian",
            "af": "Afrikaans",
            "bs": "Bosnian",
            "am": "Amharic",
            "bn": "Bengali",
            "gl": "Galician",
            "gu": "Gujarati",
            "he": "Hebrew",
            "hu": "Hungarian",
            "ka": "Georgian",
            "ml": "Malayalam",
            "mr": "Marathi",
            "mt": "Maltese",
            "mk": "Macedonian",
            "ps": "Pashto",
            "si": "Sinhala",
            "sk": "Slovak",
            "sl": "Slovene",
            "so": "Somali",
            "su": "Sundanese",
            "sw": "Swahili",
            "ta": "Tamil",
            "te": "Telugu",
            "zu": "Zulu",
            "cy": "Welsh",
            "kk": "Kazakh",
            "lo": "Lao",
            "lv": "Latvian",
            "hr": "Croatian",
            "el": "Greek",
            "is": "Icelandic",
            "cs": "Czech",
            "et": "Estonian",
            "fil": "Filipino",
            "ga": "Irish",
            "lt": "Lithuanian",
            "iu": "Inuktitut",
            "mn": "Mongolian",
            "ne": "Nepali",
            "nb": "Norwegian Bokmål",
            "ur": "Urdu",
            "uz": "Uzbek",
            "jv": "Javanese",
            "kn": "Kannada",
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
    "en": "If you like the service, please donate to support the site",
    "es": "Si te gusta el servicio, por favor dona para apoyar el sitio",
    # أضف المزيد من الترجمات هنا
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"]
        voice = request.form["voice"]
        audio_stream = generate_audio(text, voice)
        return send_file(audio_stream, mimetype="audio/wav", as_attachment=True, download_name="output.wav")
    
    return render_template("index.html", translations=translations)

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)  # هذا البورت يمكن تعديله إذا كنت تستخدم منصة مثل Railway
    app.run(host="0.0.0.0", port=int(port))
