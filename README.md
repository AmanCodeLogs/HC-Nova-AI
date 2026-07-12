# HealthCurve Nova AI - Backend API

Production-ready Python Flask backend for **HealthCurve Nova AI**, built for the HACKHAZARDS '26 hackathon. This API serves as the central orchestration layer—connecting a mobile Expo client to Sarvam AI Document Intelligence and LangChain-managed Gemini models for structured medical tracking.

## 🛠️ Tech Stack
* **Framework:** Python & Flask
* **Security:** Flask-CORS (Cross-Origin Resource Sharing)
* **Vision & OCR:** Sarvam AI Python SDK (`document_digitization`)
* **LLM Orchestration:** LangChain (`langchain-google-genai`)
* **AI Model:** Google Gemini 1.5 Flash
* **Production Server:** Gunicorn

## ⚙️ Core Architecture
1. **Prescription Digitization (Sarvam AI):** Receives uploaded prescription image files from the mobile app and runs layout-aware Document Intelligence OCR to read localized medical text.
2. **Entity Extraction (LangChain + Gemini):** Parses the messy OCR text through a structured LangChain prompt to output a predictable JSON array of medication names, exact dosages, and times.
3. **Patient Portal (Gemini):** Provides an interactive companion chat endpoint allowing patients to query their dosage timelines safely.

## 🚀 Quick Start & Installation

1. **Clone the project repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/nova-backend.git](https://github.com/YOUR_USERNAME/nova-backend.git)
   cd nova-backend

##Install the required packages:

Bash
pip install -r requirements.txt
Configure your environment keys:

Bash
export SARVAM_API_KEY="your_sarvam_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
Launch the API locally:

Bash
python app.py

##🌐 Endpoints
📋 Process Prescription
URL: /api/ocr/process

Method: POST

Payload: multipart/form-data with an image file attached to the prescription key.

Returns: A JSON array containing structured medication cards (medicine, dosage, time, instructions, taken).

##💬 Patient Chat Consultation
URL: /api/chat

Method: POST

Payload: application/json mapping { "message": "Your question here" }

Returns: { "text": "Nova AI response string" }
