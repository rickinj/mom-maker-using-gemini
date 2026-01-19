# mom_audio_processing.py
import os
import re
import random
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from google.cloud import bigquery, storage
from vertexai import init
from vertexai.generative_models import GenerativeModel, Part

load_dotenv()

# --- CONFIGURATION ---
BIGQUERY_PROJECT_ID = os.environ.get("BIGQUERY_PROJECT_ID", "your-project-id")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "your-dataset-name")
BIGQUERY_TABLE = os.environ.get("BIGQUERY_TABLE", "your-table-name")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "your-gcs-bucket-name")

# --- CLIENT INITIALIZATION ---
try:
    bigquery_client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    storage_client = storage.Client()
    init(project=BIGQUERY_PROJECT_ID, location="us-central1")
    gemini_model = GenerativeModel(GEMINI_MODEL)
    print("✅ Clients initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing clients: {e}")
    raise SystemExit(1)


# --- HELPERS ---
def generate_meeting_id() -> int:
    return random.randint(10000, 99999)


def upload_file_to_gcs(local_path: str, bucket_name: str, dest_blob_name: str):
    mime_type, _ = mimetypes.guess_type(local_path)
    mime_type = mime_type or "application/octet-stream"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(dest_blob_name)

    print(f"⬆️ Uploading {local_path} → gs://{bucket_name}/{dest_blob_name}")
    blob.upload_from_filename(local_path)

    return f"gs://{bucket_name}/{dest_blob_name}", mime_type


def parse_sections(text: str) -> Dict[str, str]:
    """
    Safely parses Gemini output using delimiters.
    """
    transcript = ""
    mom = ""

    if "---TRANSCRIPT---" in text and "---MOM---" in text:
        parts = text.split("---MOM---", 1)
        transcript = parts[0].replace("---TRANSCRIPT---", "").strip()
        mom = parts[1].strip()

    return {
        "transcript": transcript,
        "mom": mom
    }


# --- MAIN PROCESSING FUNCTION ---
def transcribe_and_analyze_audio(gcs_uri: str, mime_type: str = None) -> Dict[str, Any]:
    mime_type = mime_type or mimetypes.guess_type(gcs_uri)[0] or "audio/wav"
    print(f"🎧 Starting transcription + MoM generation for {gcs_uri} ({mime_type})")

    audio_part = Part.from_uri(gcs_uri, mime_type=mime_type)

    unified_prompt = """
You are an expert meeting assistant.

TASK 1: TRANSCRIPT
- Listen carefully to the full audio.
- Produce a clear, corrected transcript.
- Label speakers clearly.
- Keep original meaning.

TASK 2: MINUTES OF MEETING (MoM)
- Create professional, well-structured Minutes of Meeting.
- Use headings and bullet points.
- Include (if available):
  Date, Participants, Agenda, Key Discussion Points,
  Decisions Taken, Action Items, Next Steps.

OUTPUT FORMAT (VERY IMPORTANT):
Return the output EXACTLY in this format:

---TRANSCRIPT---
<full transcript here>

---MOM---
<formatted Minutes of Meeting here>

Do NOT include anything else.
"""

    try:
        response = gemini_model.generate_content([audio_part, unified_prompt])
        raw = response.text.strip()

        parsed = parse_sections(raw)

        if not parsed["transcript"] or not parsed["mom"]:
            print("⚠️ Failed to parse Gemini output using delimiters.")
            return {"error": "Parsing failed", "raw_output": raw}

        return parsed

    except Exception as e:
        print(f"❌ Error during Gemini processing: {e}")
        return {"error": str(e)}


# --- BIGQUERY INSERT ---
def insert_to_bigquery(
    data: dict,
    meeting_id: int,
    gs_uri: str
):
    table_id = f"{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

    row = [{
        "meeting_id": str(meeting_id),
        "gs_uri": gs_uri,
        "transcript": data.get("transcript", ""),
        "mom": data.get("mom", ""),
        "created_at": datetime.utcnow().isoformat()
    }]

    print(f"📦 Uploading MoM for Meeting ID {meeting_id} to BigQuery...")

    errors = bigquery_client.insert_rows_json(table_id, row)
    if errors:
        raise RuntimeError(f"❌ BigQuery insert failed: {errors}")

    print("✅ Transcript and MoM inserted successfully.")


# --- MAIN PIPELINE ---
def process_local_file_and_upload(
    local_path: str,
    bucket_name: str = GCS_BUCKET,
    dest_blob_name: str = None
):
    if dest_blob_name is None:
        dest_blob_name = (
            f"mom_audio/{Path(local_path).stem}_"
            f"{random.randint(1000,9999)}{Path(local_path).suffix}"
        )

    gs_uri, mime_type = upload_file_to_gcs(local_path, bucket_name, dest_blob_name)

    result = transcribe_and_analyze_audio(gs_uri, mime_type)

    meeting_id = generate_meeting_id()

    if "error" not in result:
        insert_to_bigquery(result, meeting_id, gs_uri)

    return {
        "gs_uri": gs_uri,
        "meeting_id": meeting_id,
        "result": result
    }


if __name__ == "__main__":
    local_file = "sample_audio.wav"
    if os.path.exists(local_file):
        print("🚀 Starting local audio processing pipeline...")
        process_local_file_and_upload(local_file)
    else:
        print("⚠️ sample_audio.wav not found.")
