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
    "fr": "Si vous aimez le service, veuillez faire un don pour soutenir le site",
    "de": "Wenn Ihnen der Service gefällt, spenden Sie bitte, um die Seite zu unterstützen",
    "zh": "如果您喜欢此服务，请捐款支持本网站",
    "ja": "このサービスが気に入ったら、サイトをサポートするために寄付してください",
    "ko": "서비스가 마음에 드셨다면, 사이트를 지원하기 위해 기부해주세요",
    "ru": "Если вам нравится сервис, пожалуйста, сделайте пожертвование для поддержки сайта",
    "pt": "Se você gosta do serviço, por favor doe para apoiar o site",
    "it": "Se ti piace il servizio, per favore dona per supportare il sito",
    "tr": "Hizmeti beğendiyseniz, siteyi desteklemek için bağış yapın",
    "pl": "Jeśli podoba Ci się ta usługa, przekaż darowiznę, aby wesprzeć stronę",
    "nl": "Als je de service leuk vindt, doneer dan om de site te ondersteunen",
    "sv": "Om du gillar tjänsten, vänligen donera för att stödja webbplatsen",
    "fi": "Jos pidät palvelusta, lahjoita tukemaan sivustoa",
    "no": "Hvis du liker tjenesten, vennligst doner for å støtte nettstedet",
    "da": "Hvis du kan lide tjenesten, bedes du donere for at støtte webstedet",
    "hi": "यदि आपको सेवा पसंद है, तो कृपया साइट का समर्थन करने के लिए दान करें",
    "id": "Jika Anda menyukai layanan ini, silakan donasi untuk mendukung situs ini",
    "vi": "Nếu bạn thích dịch vụ này, hãy quyên góp để hỗ trợ trang web",
    "th": "หากคุณชอบบริการนี้ โปรดบริจาคเพื่อสนับสนุนเว็บไซต์",
    "ms": "Jika anda suka perkhidmatan ini, sila menderma untuk menyokong laman web",
    "fa": "اگر از این خدمات راضی هستید، لطفاً برای حمایت از سایت کمک مالی کنید",
    "uk": "Якщо вам подобається сервіс, будь ласка, пожертвуйте, щоб підтримати сайт",
    "ro": "Dacă vă place serviciul, vă rugăm să donați pentru a susține site-ul",
    "sr": "Ако вам се допада услуга, молимо вас да донирате за подршку сајту",
    "bg": "Ако харесвате услугата, моля дарете, за да подкрепите сайта",
    "az": "Xidmət xoşunuza gəldisə, saytı dəstəkləmək üçün ianə edin",
    "my": "သင်သက်ဆိုင်သောဝန်ဆောင်မှုကြိုက်လျှင်၊ဆိုဒ်ကိုထောက်ပံ့ရန်လှူဒါန်းပါ",
    "ca": "Si t'agrada el servei, fes una donació per donar suport al lloc",
    "sq": "Nëse ju pëlqen shërbimi, ju lutemi dhuroni për të mbështetur faqen",
    "af": "As u van die diens hou, skenk asseblief om die webwerf te ondersteun",
    "bs": "Ako vam se sviđa usluga, molimo vas da donirate za podršku sajtu",
    "am": "አገልግሎቱን እናውቀው እንደሆንህ ስፖርት ማቅረብ እባኮትን አትርሱ",
    "bn": "যদি আপনি পরিষেবাটি পছন্দ করেন তবে সাইটটি সমর্থন করতে অনুদান দিন",
    "gl": "Se che gusta o servizo, doe para apoiar o sitio",
    "gu": "જો તમને સેવા ગમે છે, તો સાઇટને ટેકો આપવા માટે દાન કરો",
    "he": "אם אתה אוהב את השירות, אנא תרום כדי לתמוך באתר",
    "hu": "Ha tetszik a szolgáltatás, kérjük, adományozzon a webhely támogatásához",
    "ka": "თუ თქვენ მოგწონთ ეს სერვისი, გთხოვთ შეიტანოთ ნაჩუქარი საიტზე",
    "ml": "നിങ്ങൾക്ക് ഈ സേവനം ഇഷ്ടമാണെങ്കിൽ, ദയവായി സൈറ്റിനെ പിന്തുണയ്‌ക്കാൻ ദാനമൊതുക്കുക",
    "mr": "तुम्हाला सेवा आवडत असल्यास, कृपया साइटला मदत करण्यासाठी दान करा",
    "mt": "Jekk jogħġbok, donawha biex tappoġġja s-sit",
}

# العرض للقائمة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# عرض نتائج التحويل
@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    text = request.form.get('text')
    voice = request.form.get('voice')

    if not text:
        return "Error: No text provided!", 400

    audio = generate_audio(text, voice)
    if audio:
        return send_file(audio, as_attachment=True, download_name="converted_audio.wav", mimetype="audio/wav")
    else:
        return "Error: Failed to generate audio!", 500

if __name__ == "__main__":
    # استخدام البورت من المتغيرات البيئية الخاصة بـ Railway
    port = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
