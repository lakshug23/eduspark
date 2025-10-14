# 📚 EduSpark - Automated Educational Video Generator

EduSpark is a full-stack Flask-based application that:
- Uses **Google Gemini** to generate engaging educational scripts
- Converts them to **natural-sounding speech** with **ElevenLabs**
- Creates short **educational videos** via **Shotstack**
- Sends the final video via **WhatsApp** using **Twilio**

---

## 🚀 Features

- ✅ Script generation from subject/topic using Gemini
- ✅ Text-to-speech using ElevenLabs
- ✅ Audio + title video generation with Shotstack
- ✅ WhatsApp delivery of the video using Twilio
- ✅ Clean frontend interface (HTML/JS)

---

## 🧠 Tech Stack

| Purpose            | Technology         |
|--------------------|--------------------|
| Backend API        | Flask              |
| Script Generation  | Google Gemini API  |
| Text-to-Speech     | ElevenLabs API     |
| Video Creation     | Shotstack API      |
| Messaging          | Twilio (WhatsApp)  |
| File Storage (Optional) | Google Drive API |
| Hosting (Dev)      | Local / Google IDX |

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
 git clone https://github.com/your-username/eduspark.git
 cd eduspark
```

### 2. Create a virtual environment

```bash
 python3 -m venv myenv
 source myenv/bin/activate
```

### 3. Install dependencies

```bash
 pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root:

```env
 GEMINI_API_KEY=your_google_gemini_api_key
 ELEVENLABS_API_KEY=your_elevenlabs_api_key
 SHOTSTACK_API_KEY=your_shotstack_api_key
 TWILIO_SID=your_twilio_sid
 TWILIO_AUTH_TOKEN=your_twilio_auth_token
 TWILIO_PHONE=whatsapp:+your_twilio_number
```

---

## ▶️ Demo

[![Watch the demo](https://img.youtube.com/vi/w__0HgkNMbI/0.jpg)](https://youtu.be/w__0HgkNMbI)

---

## ▶️ Run the App

```bash
 python app.py
```

Visit `http://localhost:5000` in your browser.

---

## 📤 Upload Audio to Google Drive (Optional)

If Shotstack cannot fetch audio from localhost, the app uses Google Drive:
- Upload the audio file to Drive
- Make it public
- Use the `https://drive.google.com/uc?export=download&id=FILE_ID` format for sharing

---

## 🙌 Credits

- [Google Gemini](https://ai.google.dev/)
- [ElevenLabs](https://www.elevenlabs.io/)
- [Shotstack](https://shotstack.io/)
- [Twilio](https://www.twilio.com/)
- [Flask](https://flask.palletsprojects.com/)

---

## Snapshots

<img src="Screenshot 2025-04-06 at 9.23.06 PM.png" alt="EduSpark Screenshot 1" width="600"/>
<img src="Screenshot 2025-04-06 at 9.23.37 PM.png" alt="EduSpark Screenshot 2" width="600"/>
<img src="Screenshot 2025-04-06 at 9.24.04 PM.png" alt="EduSpark Screenshot 3" width="600"/>
<img src="Screenshot 2025-04-06 at 9.24.29 PM.png" alt="EduSpark Screenshot 4" width="600"/>

---