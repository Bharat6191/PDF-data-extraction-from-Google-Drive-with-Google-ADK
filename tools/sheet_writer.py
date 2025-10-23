from google.adk.tools import BaseTool
from oauth2client.service_account import ServiceAccountCredentials
import gspread


class SheetWriterTool(BaseTool):
    name = "sheet_writer"
    description = (
        "Writes structured invoice data into Google Sheet with ordered columns."
    )

    def __init__(self, service_account_path, sheet_id):
        print("📝 [SheetWriterTool] Initialized")
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            service_account_path, scope  # type: ignore
        )
        self.client = gspread.authorize(creds)  # type: ignore
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def ensure_headers(self, fields):
        """Forcefully write headers to the first row if missing."""
        try:
            existing = self.sheet.row_values(1)  # ✅ Get actual first row
            if not existing:
                print("📝 [SheetWriterTool] First row empty — writing headers...")
                self.sheet.update(
                    "A1", [fields]  # type: ignore
                )  # 🚀 This is more reliable than insert_row
            else:
                print(f"ℹ️ [SheetWriterTool] Headers already exist: {existing}")
        except Exception as e:
            print(f"❌ [SheetWriterTool] Failed to ensure headers: {e}")

    def run(self, data: dict, fields: list):
        self.ensure_headers(fields)
        row = [data.get(field, "") for field in fields]
        print(f"📝 [SheetWriterTool] Appending row: {row}")
        try:
            self.sheet.append_row(row)
            print("✅ [SheetWriterTool] Row successfully added.")
            return {"status": "success", "data": row}
        except Exception as e:
            print(f"❌ [SheetWriterTool] Failed to append row: {e}")
            return {"status": "error", "error": str(e)}
