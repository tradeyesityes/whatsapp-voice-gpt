from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
import requests
import whisper
from pydub import AudioSegment

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

model = whisper.load_model("base")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_voice():
    resp = MessagingResponse()
    msg = resp.message()

    media_url = request.form.get('MediaUrl0')
    media_type = request.form.get('MediaContentType0')

    if media_url and 'audio' in media_type:
        try:
            audio_data = requests.get(media_url)
            with open("voice.ogg", "wb") as f:
                f.write(audio_data.content)

            sound = AudioSegment.from_file("voice.ogg", format="ogg")
            sound.export("voice.wav", format="wav")

            result = model.transcribe("voice.wav", language="ar")
            transcribed_text = result["text"]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": transcribed_text}]
            )
            reply = completion.choices[0].message.content.strip()

            msg.body(f"🗣️ سؤالك: {transcribed_text}\n\n🤖 الجواب: {reply}")
        except Exception as e:
            msg.body("❌ حدث خطأ في المعالجة.")
    else:
        msg.body("🎤 أرسل رسالة صوتية فقط وسأرد عليك!")

    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "🚀 WhatsApp Arabic Voice AI is Running"
