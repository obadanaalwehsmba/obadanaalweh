# استخدم صورة Ubuntu حديثة
FROM ubuntu:22.04

# تحديث الحزم وتثبيت الأدوات المطلوبة
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3-pip \
    python3-dev \
    libsndfile1 \
    && apt-get clean

# نسخ ملف المتطلبات إلى المجلد المناسب
COPY requirements.txt /app/

# تعيين مجلد العمل
WORKDIR /app

# تثبيت المكتبات من ملف requirements.txt
RUN pip3 install -r requirements.txt

# نسخ باقي الكود إلى المجلد
COPY . /app/

# تنفيذ التطبيق
CMD ["python3", "main.py"]