from google.adk.tools import BaseTool
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
from PyPDF2 import PdfReader


class DriveReaderTool(BaseTool):
    name = "drive_reader"
    description = (
        "Reads PDF file from Google Drive using file_id and returns its text content."
    )

    def __init__(self, service_account_path):
        print("📥 [DriveReaderTool] Initialized")
        creds = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        self.drive_service = build("drive", "v3", credentials=creds)

    def run(self, file_id: str):
        print(f"📥 [DriveReaderTool] Reading file_id={file_id}")
        request = self.drive_service.files().get_media(fileId=file_id)
        pdf_stream = io.BytesIO(request.execute())

        reader = PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        print(f"📥 [DriveReaderTool] Extracted {len(text)} characters from file.")
        return text
