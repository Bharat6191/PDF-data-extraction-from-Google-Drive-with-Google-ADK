import os
import json
import re
import time
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.genai import Client

from tools.drive_reader import DriveReaderTool
from tools.sheet_writer import SheetWriterTool

# ---------------- CONFIGURATION ----------------
load_dotenv()

SERVICE_ACCOUNT = "service_account.json"
SHEET_ID = os.getenv("SHEET_ID")
FOLDER_ID = os.getenv("FOLDER_ID")
PROCESSED_FILE = "processed_invoices.txt"
GEMINI_MODEL = "models/gemini-2.5-flash"

# Load API Key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# Initialize tools
drive_tool = DriveReaderTool(SERVICE_ACCOUNT)
sheet_tool = SheetWriterTool(SERVICE_ACCOUNT, SHEET_ID)
client = Client(api_key=os.environ["GOOGLE_API_KEY"])

# ---------------- FIELDS ----------------
FIELDS = [
    "file_name",
    "invoice_number",
    "account_number",
    "billing_date",
    "services_from",
    "services_to",
    "previous_balance",
    "payments",
    "balance_forward",
    "regular_monthly_charges",
    "taxes_fees_other_charges",
    "new_charges",
    "amount_due_date",
    "total_amount_due",
    "company_name",
    "company_address",
    "bandwidth",
    "port_id",
    "circuit_id",
    "evc_area_type",
    "ipv4_25_price",
    "ipv4_24_price",
    "equipment_charges",
    "sales_tax_city",
    "sales_tax_county",
    "sales_tax_state",
]


# ---------------- UTILS ----------------
def list_pdfs_in_folder(folder_id):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    service = build("drive", "v3", credentials=creds)
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = (
        service.files().list(q=query, fields="files(id, name, md5Checksum)").execute()
    )
    return results.get("files", [])


def load_processed_keys():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_processed_key(key):
    with open(PROCESSED_FILE, "a") as f:
        f.write(key + "\n")


def build_unique_key(data: dict, fallback: str):
    """Build unique key from important fields, fallback to file ID if empty."""
    invoice_number = data.get("invoice_number", "").strip()
    account_number = data.get("account_number", "").strip()
    total_amount_due = data.get("total_amount_due", "").strip()
    billing_date = data.get("billing_date", "").strip()

    key_fields = [invoice_number, account_number, total_amount_due, billing_date]
    if any(key_fields):
        return "::".join([f or "NA" for f in key_fields])
    else:
        return f"FALLBACK::{fallback}"


def extract_invoice_data(pdf_text):
    """Send text to Gemini and extract structured fields with interrupt handling."""
    field_json_template = "{\n" + ",\n".join([f'  "{f}": ""' for f in FIELDS]) + "\n}"
    prompt = f"""
    You are given the text of an invoice PDF.
    Extract and return ONLY valid JSON in this exact structure:
    {field_json_template}

    If a field is not present, leave its value empty.

    Invoice text:
    {pdf_text[:8000]}
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
        )
    except KeyboardInterrupt:
        print("\n🛑 Gemini call interrupted by user (Ctrl+C). Exiting gracefully...")
        raise

    raw = response.text
    print("🤖 Gemini raw response:", raw)

    try:
        return json.loads(raw)  # type: ignore
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S)  # type: ignore
        return json.loads(m.group(0)) if m else {}


# ---------------- PROCESS FILES ----------------
def process_new_files(processed_keys):
    print("📂 Checking Drive folder for new files...")
    files = list_pdfs_in_folder(FOLDER_ID)

    for file in files:
        file_id = file["id"]
        file_name = file["name"]
        file_hash = file.get("md5Checksum", file_id)

        print(f"📄 Checking file: {file_name}")
        pdf_text = drive_tool.run(file_id)

        if not pdf_text.strip():
            print(f"⚠️ No text found in {file_name}. Skipping.")
            continue

        extracted_data = extract_invoice_data(pdf_text)
        unique_key = build_unique_key(extracted_data, fallback=file_hash)

        if unique_key in processed_keys:
            print(f"⏩ Skipping already processed invoice (key={unique_key})")
            continue

        # Ensure all fields exist
        for f in FIELDS:
            if f not in extracted_data:
                extracted_data[f] = ""

        extracted_data["file_name"] = file_name

        # Write to Google Sheet
        sheet_tool.run(extracted_data, FIELDS)

        # Mark as processed
        processed_keys.add(unique_key)
        save_processed_key(unique_key)

        print(f"✅ Successfully processed invoice (key={unique_key}): {file_name}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    processed_keys = load_processed_keys()
    print(f"🚀 Loaded {len(processed_keys)} processed invoice keys from disk.")

    try:
        while True:
            process_new_files(processed_keys)
            print("⏳ Waiting 60 seconds for next check...\n")
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 Received Ctrl+C — shutting down gracefully...")
        print(
            f"💾 {len(processed_keys)} invoice keys are already saved in {PROCESSED_FILE}."
        )
        print("✅ Safe to restart later — no duplicates will be processed.")
        exit(0)
