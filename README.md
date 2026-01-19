# 📝 Minutes of Meeting (MoM) Generator using GenAI

An end-to-end **Generative AI–powered Minutes of Meeting (MoM)** system that converts meeting audio into a clean transcript and professionally structured MoM using **Google Gemini**, **Google Cloud Storage**, **BigQuery**, and a simple web interface.

---

## 🚀 Features

- 🎧 Upload meeting audio via a web UI  
- 🧠 Automatic transcription using Gemini multimodal model  
- 📝 AI-generated Minutes of Meeting (MoM) with clear structure  
- 📄 Clean Markdown → HTML rendering for easy readability  
- ☁️ Audio stored securely in Google Cloud Storage  
- 🗃️ Transcript and MoM persisted in BigQuery for future access  
- 🔁 Robust delimiter-based parsing for long audio files  
- 💼 Designed for HR, admin, and internal meeting documentation  

---

## 🏗️ Architecture Overview

    Frontend (HTML + JS)
    ↓
    Flask Backend (API)
    ↓
    Temporary Local Storage
    ↓
    Google Cloud Storage (GCS)
    ↓
    Gemini (Vertex AI)
    ↓
    Transcript + MoM
    ↓
    BigQuery (Persistence)
    ↓
    Rendered to Frontend

---

## 🛠️ Tech Stack

### Frontend
- HTML, CSS, Vanilla JavaScript  
- Markdown rendering using `marked.js`

### Backend
- Python  
- Flask (API layer)

### Cloud & GenAI
- Google Cloud Storage (audio storage)  
- Google Vertex AI – Gemini 2.5 Flash  
- Google BigQuery (data persistence)

---

## 📂 Project Structure

    ├── app.py # Flask backend
    ├── mom_audio_processing.py # Audio → Gemini → MoM pipeline
    ├── templates/
    │ └── index.html # Frontend UI
    ├── .env # Environment variables (not committed)
    └── README.md

---

## ⚙️ Environment Variables

Create a `.env` file with the following variables  
(values are not shared for security reasons):

```env
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET=your-dataset
BIGQUERY_TABLE=your-table
GCS_BUCKET=your-bucket-name
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

⚠️ The `.env` file is intentionally excluded from version control.

---

## ▶️ How It Works

1. User uploads an audio file (`.wav`, `.mp3`, `.m4a`, etc.)

2. Flask backend:
   - Saves audio temporarily  
   - Uploads it to Google Cloud Storage  
   - Sends audio to Gemini using a multimodal prompt  

3. Gemini returns output in a delimiter-based format:

---TRANSCRIPT---
...
---MOM---
...


4. Backend safely parses the output

5. Transcript and MoM are:
   - Stored in BigQuery  
   - Returned to the frontend  

6. Frontend renders:
   - MoM as formatted HTML  
   - Transcript as plain text  

---

## 🧠 Why Delimiter-Based Parsing?

Instead of relying on strict JSON output from the LLM (which often fails for long transcripts), this project uses explicit delimiters:

---TRANSCRIPT---
---MOM---


### Benefits
- More reliable for long audio  
- No JSON parsing failures  
- Production-grade GenAI design pattern  

---

## 📊 BigQuery Schema

| Column Name | Data Type |
|------------|-----------|
| meeting_id | STRING    |
| gs_uri     | STRING    |
| transcript | STRING    |
| mom        | STRING    |
| created_at | TIMESTAMP |

---


This enables:
- Historical access to meetings  
- No need to re-run Gemini  
- Easy future HR dashboards and analytics  

---

## 📦 Supported Audio Formats

- `.wav`  
- `.mp3`  
- `.flac`  
- `.m4a`  
- `.ogg`  

**Max upload size:** 200 MB  

---

## ▶️ Running the Project Locally

```bash
pip install -r requirements.txt
python app.py
```

Then open:
```bash
http://localhost:8080
```

---

## 🔐 Security & Permissions

- Uses Google service account authentication  
- Vertex AI accesses audio via managed service agents  
- GCS access controlled using IAM roles  
- No secrets committed to GitHub  

---

## 📈 Future Improvements

- HR dashboard to view past MoMs  
- User authentication and role-based access  
- Export MoM to PDF / DOCX  
- Speaker diarization improvements  
- Migration from Flask to FastAPI  
- Deployment on Google Cloud Run  

---

## 🎯 Ideal Use Cases

- HR meeting documentation  
- Council / board meetings  
- Internal team meetings  
- Interview panel discussions  
- Operations and compliance logs  

---

## 🧑‍💻 Author Notes

This project was built to demonstrate:

- Practical GenAI system design  
- Real-world cloud integration  
- Robust handling of LLM outputs  
- Clean separation of frontend, backend, and AI logic  

---

## ⭐ Like this project?

Feel free to ⭐ the repository or fork it to extend further.
