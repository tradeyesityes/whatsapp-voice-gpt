import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pydub import AudioSegment
import openai
import whisper
from dotenv import load_dotenv
import requests

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# إعداد المفاتيح
openai.api_key = os.getenv("OPENAI_API_KEY")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# تحميل نموذج Whisper
model = whisper.load_model("base")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Voice AI is running."

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # الحصول على بيانات من Twilio
    num_media = int(request.form.get("NumMedia", 0))
    from_number = request.form.get("From")
    response = MessagingResponse()

    if num_media == 0:
        response.message("الرجاء إرسال رسالة صوتية.")
        return str(response)

    # الحصول على رابط الوسائط (الصوت)
    media_url = request.form.get("MediaUrl0")
    media_content_type = request.form.get("MediaContentType0")

    if not media_url or "audio" not in media_content_type:
        response.message("يرجى إرسال ملف صوتي فقط.")
        return str(response)

    # تحميل ملف الصوت
    audio_file = "input.ogg"
    r = requests.get(media_url)
    with open(audio_file, "wb") as f:
        f.write(r.content)

    # تحويله إلى wav باستخدام pydub
    wav_file = "converted.wav"
    sound = AudioSegment.from_file(audio_file)
    sound.export(wav_file, format="wav")

    # تحويل الصوت إلى نص
    result = model.transcribe(wav_file)
    text = result["text"]

    # إرسال النص إلى GPT للرد
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}]
    )

    reply = gpt_response["choices"][0]["message"]["content"]
    response.message(reply)
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
