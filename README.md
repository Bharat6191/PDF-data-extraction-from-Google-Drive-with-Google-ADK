# 🧾 PDF Agent — Google Drive + Sheets + Vertex AI Automation

`pdf-agent` is a Python-based automation tool that:
- 📥 Reads and extracts text from PDF files stored in **Google Drive**  
- 📝 Writes structured data to **Google Sheets**  
- 🧠 (Optional) Uses **Vertex AI** Gemini models to process and understand documents  

This project helps automate document processing workflows using Google Cloud services.

---

## 🚀 Features

- ✅ Read PDF content directly from Google Drive using its file ID  
- ✅ Extract and process text content with Python  
- ✅ Write structured data into Google Sheets in an ordered format  
- 🤖 (Optional) Use Gemini models from Vertex AI to analyze PDF content  

---

## 🧰 1. Prerequisites

Before setting up the project, make sure you have:

- A **Google Cloud project** with the following APIs enabled:
  - [x] 📄 Google Drive API  
  - [x] 📊 Google Sheets API  
  - [x] 🧠 Vertex AI API (for Gemini models)

- A **Service Account** with:
  - Access to the PDF folder in Google Drive
  - Editor permission on the target Google Sheet
  - A downloaded JSON key file (e.g. `service_account.json`)

---

## 🪙 How to Create and Download `service_account.json`

Follow these steps carefully:

1. Go to 👉 [Google Cloud Console](https://console.cloud.google.com)  
2. Select or create a **Google Cloud Project**.  
3. Enable these APIs:
   - Google Drive API
   - Google Sheets API
   - Vertex AI API (optional)
4. In the left menu, go to **“IAM & Admin” → “Service Accounts”**.  
5. Click **“+ Create Service Account”**.  
6. Give it a name (e.g., `pdf-agent-sa`) and click **Create**.  
7. On the “Grant this service account access” step:
   - Assign the **Editor** role.
8. Click **Done**.  
9. You’ll now see your service account in the list. Click on it.  
10. Go to the **“Keys”** tab → **“Add Key” → “Create new key”**.  
11. Choose **JSON** and click **Create**.  
12. A file named something like `your-project-xxxx.json` will be downloaded — this is your **`service_account.json`**.

👉 Move this file to the root of your project:

---

## 🏗️ 2. Project Structure

pdf-agent/
├── venv/                     # Virtual environment (not committed to Git)
├── main.py                   # Entry point for the agent
├── tools/                    # Custom tools for Google services
│   ├── drive_reader.py       # Reads PDFs from Google Drive
│   └── sheet_writer.py       # Writes data to Google Sheets
├── service_account.json      # Google service account credentials
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
└── requirements.txt          # Python dependencies

## ⚙️ 3. Setup Instructions

### Step 1: 📦 Clone the Repository

git clone https://github.com/Bharat6191/PDF-data-extraction-from-Google-Drive-with-Google-ADK.git
cd pdf-agent

### Step 2: 🐍 Create and Activate a Virtual Environment

A virtual environment helps you manage dependencies cleanly without affecting system-wide Python packages.

🖥️ On macOS / Linux:

python3 -m venv venv
source venv/bin/activate


🪟 On Windows (Command Prompt):

python -m venv venv
venv\Scripts\activate

Once activated, your terminal should show something like:

(venv) $

To deactivate the environment anytime:

deactivate

### Step 3: 📥 Install Dependencies

pip install -r requirements.txt

### Step 4: 🔐 Add Google Service Account Key

Place your downloaded service_account.json file inside the project root:

pdf-agent/
└── service_account.json


### Step 5: 🌐 Share Drive Folder and Sheet

Share your Google Drive folder (containing PDFs) with the service account email.  
Share your Google Sheet with **Editor** access to the same service account.

---

## 🧠 4. How It Works

### 📥 Drive Reader (`tools/drive_reader.py`)
- Authenticates with the service account  
- Reads PDF from Google Drive using `file_id`  
- Extracts text content using `PyPDF2`

### 📝 Sheet Writer (`tools/sheet_writer.py`)
- Connects to Google Sheets using service account credentials  
- Writes structured data into pre-defined columns or headers  

### 🤖 (Optional) Vertex AI
Integrate Gemini models for:
- Summarization  
- Document classification  
- Intelligent data extraction  

### 🧪 5. Running the Project

Run the Main Script

python main.py

### 6. Environment Variables

GOOGLE_API_KEY=YOUR_OPTIONAL_API_KEY_FOR_GEMINI_IF_NOT_USING_SERVICE_ACCOUNT
SHEET_ID=YOUR_GOOGLE_SHEET_ID
FILE_ID=A_SINGLE_PDF_FILE_ID_FOR_TESTING
FILE_NAME=Example_Document.pdf
FOLDER_ID=YOUR_GOOGLE_DRIVE_FOLDER_ID



