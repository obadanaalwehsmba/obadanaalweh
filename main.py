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
    "hu": "Ha tetszik a szolgáltatás, kérjük, adományozzon a webhely támogatására",
    "ka": "თუ მოგწონთ სერვისი, გთხოვთ, დაეხმაროთ საიტის მხარდაჭერას",
    "ml": "സേവനം നിങ്ങള്‍ക്ക് ഇഷ്ടമായെങ്കില്‍, വെബ്‌സൈറ്റിനെ പിന്തുണയ്ക്കാന്‍ ദാനം ചെയ്യുക",
    "mr": "सेवा आवडल्यास, साइट समर्थनासाठी देणगी द्या",
    "mt": "Jekk jogħġbok, jekk tixtieq, agħmel donazzjoni biex tappoġġja s-sit",
    "mk": "Доколку ви се допаѓа услугата, ве молиме донирајте за да го поддржите сајтот",
    "ps": "که تاسو له خدمت څخه خوښ ياست، نو مهرباني وکړئ د ځای ملاتړ لپاره مرسته وکړئ",
    "si": "ඔබට සේවාව පැහැදිලි නම්, කරුණාකර පිටුවට සහාය විය යුතුයි",
    "sk": "Ak sa vám služba páči, prosím, darujte na podporu stránky",
    "sl": "Če vam je storitev všeč, prosimo, darujte za podporo spletnemu mestu",
    "so": "Haddii aad adeegga ka hesho, fadlan ku tabaruc si aad u taageerto goobta",
    "su": "Lamun anjeun resep kana jasa, punten nyumbangkeun pikeun ngadukung situs",
    "sw": "Ikiwa unapenda huduma, tafadhali changia kusaidia tovuti",
    "ta": "உங்களுக்கு சேவை பிடித்திருந்தால், தயவுசெய்து தளத்தைக் காக்க நன்கொடை வழங்கவும்",
    "te": "మీకు సేవ నచ్చితే, దయచేసి వెబ్‌సైట్‌ను మద్దతు ఇవ్వడానికి విరాళం ఇవ్వండి",
    "zu": "Uma uthanda insiza, sicela unikele ukusekela isiza",
    "cy": "Os ydych chi'n hoffi'r gwasanaeth, rhoddwch i gefnogi'r safle",
    "kk": "Қызмет ұнаса, сайтты қолдауға қайырымдылық жасаңыз",
    "lo": "ຖ້າທ່ານມັກບໍລິການຂອງເວັບ, ກະລຸນາບໍລິຈາກເພື່ອສະໜັບສະໜູນເວັບໄຊ",
    "lv": "Ja jums patīk pakalpojums, lūdzu, ziedojiet, lai atbalstītu vietni",
    "hr": "Ako vam se sviđa usluga, molimo vas da donirate za podršku stranici",
    "cs": "Pokud se vám služba líbí, přispějte na podporu webu",
    "et": "Kui teile teenus meeldib, annetage saidi toetuseks",
    "fil": "Kung gusto mo ang serbisyo, mangyaring mag-donate upang suportahan ang site",
    "ga": "Má thaitníonn an tseirbhís leat, déan síntiús chun tacú leis an suíomh",
    "lt": "Jei jums patinka paslauga, paaukoti svetainės palaikymui",
    "iu": "ᐅᑕᒪᑦ ᐃᒪᓂᐅᔭᖅᑎᑦ ᐊᒻᒪᓗᒃ ᐊᑐᖏᓐᓂᒃ ᓇᖏᓐᓂᒃ ᐊᓯᒪᓕᒃ ᓄᓇᓯᐅᒃ",
    "mn": "Хэрэв танд энэ үйлчилгээ таалагдвал, сайт руу хандив өргөнө үү",
    "ne": "यदि तपाईंलाई सेवा मन पर्छ भने, साइटलाई समर्थन गर्न दान गर्नुहोस्",
    "nb": "Hvis du liker tjenesten, vennligst doner for å støtte nettstedet",
    "ur": "اگر آپ کو یہ خدمت پسند آئی تو سائٹ کی حمایت کے لئے براہ کرم چندہ دیں",
    "uz": "Agar xizmat sizga yoqsa, saytni qo‘llab-quvvatlash uchun xayriya qiling",
    "jv": "Yen sampeyan seneng karo layanan iki, mangga nyumbang kanggo ndhukung situs iki",
    "el": "Αν σας αρέσει η υπηρεσία, παρακαλώ δωρεά για να υποστηρίξετε την ιστοσελίδα",
    "is": "Ef þér líkar þjónustan, vinsamlegast doneraðu til að styðja síðuna",
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)






