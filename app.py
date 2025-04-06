from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import re
import requests
import textwrap
import base64
import uuid
import time
from moviepy.editor import VideoFileClip, AudioFileClip
from twilio.rest import Client
from google.cloud import storage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    """Authenticate the user and return a Google Drive service object."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/lakshanagopu/Downloads/client_secret_508904516084-9gdh085npel4r2jhjjr1ci2qt5o2huld.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

from googleapiclient.http import MediaFileUpload

def upload_audio_to_drive(audio_file_path):
    """Upload an audio file to Google Drive and return a public download link."""
    service = authenticate_google_drive()

    file_metadata = {'name': os.path.basename(audio_file_path)}
    media = MediaFileUpload(audio_file_path, mimetype='audio/mp3')

    # Upload the file
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    # Make the file public
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(fileId=file_id, body=permission).execute()

    # Return a direct download link
    public_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return public_url

load_dotenv()
app = Flask(__name__)

def send_video_via_whatsapp(video_url, phone_number, topic):
    # Initialize the Twilio Client with your SID and Auth Token
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    # Create and send the WhatsApp message
    message = client.messages.create(
        body=f"Here's your learning video on *{topic}* 🎓",  # Customize the message body
        media_url=[video_url],  # Ensure the video URL is valid and accessible
        from_="whatsapp:+14155238886",  # Twilio sandbox number (or your verified number for production)
        to=f"whatsapp:{phone_number}"  # The recipient's WhatsApp number (in E.164 format, i.e., +1234567890)
    )
    
    return message

# Load API keys from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")




@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.json
    subject = data["subject"]
    topic = data["topic"]
    phone = data["phone"]

    # 1. Generate script using Gemini
    prompt = f"Create a short, engaging, student-friendly script for a video lesson in {subject} on the topic: {topic}. Keep it under 300 words.Only provide the exact words to be read aloud by the speaker. Do not include headings, formatting symbols (like *, **, '\n'), scene directions, or roles like “Narrator” or “Voiceover”. The response should be plain text, ready to be spoken."
    
    gemini_resp = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
    params={"key": GEMINI_API_KEY},
    json={"contents": [{"parts": [{"text": prompt}]}]}
)
    
    # DEBUGGING LINE
    print("Gemini response:", gemini_resp.text)

    prompt1=f"Generate content for 3 slides from{gemini_resp.text},without character like *,/ or any special characters and after content of one slide has ended indicate with ';' "
    gemini_resp1 = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
    params={"key": GEMINI_API_KEY},
    json={"contents": [{"parts": [{"text": prompt1}]}]}
)
    
    gemini_data = gemini_resp.json()
    


    


    raw_parts = re.split(r'\n\s*\n', gemini_resp1.text.strip())
    if len(raw_parts) < 3:
        sentences = re.split(r'(?<=[.!?])\s+', gemini_resp1.text)
        raw_parts = [' '.join(sentences[i:i+4]) for i in range(0, len(sentences), 4)]


    slides = [textwrap.fill(part.strip(), width=100) for part in raw_parts if part.strip()]

    part1 = slides[0] if len(slides) > 0 else ""
    part2 = slides[1] if len(slides) > 1 else ""
    part3 = slides[2] if len(slides) > 2 else ""

    

# SAFETY CHECK
    if 'candidates' not in gemini_data:
        return jsonify({"status": "error", "message": "Gemini API failed", "response": gemini_data})

    script = gemini_data['candidates'][0]['content']['parts'][0]['text']

    # ELEVENLABS_API_KEY must be loaded via dotenv or set in the environment
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice = "9BWtsMINqrJLrRacOk9x"  # You can change this to any available ElevenLabs voice

    response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
    headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    },
    json={
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs TTS failed: {response.text}")

    # Save audio file
    audio_filename = f"static/audio_{uuid.uuid4().hex}.mp3"
    with open(audio_filename, "wb") as out:
        out.write(response.content)

    drive_audio_url = upload_audio_to_drive(audio_filename)
    
    slide_duration = 5
    # 3. Generate video using Shotstack
    shotstack_resp = requests.post(
        "https://api.shotstack.io/edit/stage/render",
        headers={
            "x-api-key": SHOTSTACK_API_KEY,
            "Content-Type": "application/json"
        },
        json= {
    "timeline": {
        "soundtrack": {
            "src": drive_audio_url,  # dynamic audio from ElevenLabs
            "effect": "fadeOut"
        },
        "tracks": [
            {
                "clips": [
                    {
                        "asset": {
                            "type": "text",
                            "text": topic,
                            "font": {
                                "family": "Montserrat ExtraBold",
                                "color": "#ffffff",
                                "size": 36
                            },
                            "alignment": {
                                "horizontal": "center"
                            }
                        },
                        "start": 0,
                        "length": slide_duration,
                        "transition": {
                            "in": "fade",
                            "out": "fade"
                        }
                    },
                    {
                        "asset": {
                            "type": "text",
                            "text": part1,
                            "font": {
                                "family": "Montserrat SemiBold",
                                "color": "#eeeeee",
                                "size": 28
                            },
                            "alignment": {
                                "horizontal": "center"
                            }
                        },
                        "start": slide_duration,
                        "length": slide_duration,
                        "transition": {
                            "in": "fade",
                            "out": "fade"
                        }
                    },
                    {
                        "asset": {
                            "type": "text",
                            "text": part2,
                            "font": {
                                "family": "Montserrat Medium",
                                "color": "#dddddd",
                                "size": 28
                            },
                            "alignment": {
                                "horizontal": "center"
                            }
                        },
                        "start": 2 * slide_duration,
                        "length": slide_duration,
                        "transition": {
                            "in": "fade",
                            "out": "fade"
                        }
                    },
                    {
                        "asset": {
                            "type": "text",
                            "text": part3,
                            "font": {
                                "family": "Montserrat Regular",
                                "color": "#cccccc",
                                "size": 28
                            },
                            "alignment": {
                                "horizontal": "center"
                            }
                        },
                        "start": 3 * slide_duration,
                        "length": slide_duration,
                        "transition": {
                            "in": "fade",
                            "out": "fade"
                        }
                    }
                ]
            }
        ]
    },
    "output": {
        "format": "mp4",
        "size": {
            "width": 1024,
            "height": 576
        }
    }
})

    shotstack_data = shotstack_resp.json()
    print("Shotstack response:", shotstack_data)

    # Get the render ID from the response
    render_id = shotstack_data.get("response", {}).get("id", None)
    if render_id is None:
        return jsonify({"status": "error", "message": "Render ID not found in Shotstack response", "response": shotstack_data})

    # 4. Check render status and get video URL
    video_url = None
    for _ in range(10):
        status_check = requests.get(
            f"https://api.shotstack.io/edit/stage/render/{render_id}",
            headers={"x-api-key": SHOTSTACK_API_KEY}
        )
        status_data = status_check.json()
        print("Shotstack status check response:", status_data)  # Add this

        if "response" in status_data and status_data["response"] and status_data["response"].get("status") == "done":
            video_url = status_data["response"]["url"]
            break
        time.sleep(5)
    
    if video_url is None:
        print("Error: Video URL was not fetched.")
        return jsonify({"status": "error", "message": "Video rendering failed or took too long."})
    else:
        print("Video URL fetched successfully:", video_url)
    
    
    # 5. Send the video via WhatsApp using Twilio
    send_video_via_whatsapp(video_url, phone, topic)
    message = send_video_via_whatsapp(video_url, phone, topic)
    print("Message SID:", message.sid)  # This will print the message SID returned by Twilio.

    return jsonify({"status": "success", "video_url": video_url})

if __name__ == "__main__":
    app.run(debug=True)
