# clean_up.py
import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
GCP_PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")
BQ_DATASET_ID = os.getenv("BIGQUERY_DATASET")

RESULTS_TABLE_ID = f"{GCP_PROJECT_ID}.{BQ_DATASET_ID}.tbl_mom_transcript"

# --- NEW MoM TABLE SCHEMA ---
SCHEMA = [
    bigquery.SchemaField("meeting_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("gs_uri", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("transcript", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("mom", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

def reset_table():
    client = bigquery.Client(project=GCP_PROJECT_ID)

    print(f"Deleting table if exists: {RESULTS_TABLE_ID}")
    try:
        client.delete_table(RESULTS_TABLE_ID, not_found_ok=True)
        print("Table deleted successfully.")
    except Exception as e:
        print(f"⚠️ Error deleting table: {e}")

    print(f"Creating table: {RESULTS_TABLE_ID}")
    try:
        table = bigquery.Table(RESULTS_TABLE_ID, schema=SCHEMA)
        client.create_table(table)
        print("Table created successfully with MoM schema.")
    except Exception as e:
        print(f"⚠️ Error creating table: {e}")

if __name__ == "__main__":
    reset_table()
