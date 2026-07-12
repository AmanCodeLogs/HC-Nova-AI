# HealthCurve Nova AI - Backend API

[![Render](https://img.shields.io/badge/Render-%2346E3B7.svg?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Netlify](https://img.shields.io/badge/Netlify-%2300C7B7.svg?style=for-the-badge&logo=netlify&logoColor=white)](https://www.netlify.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Sarvam AI](https://img.shields.io/badge/Sarvam_AI-orange?style=for-the-badge&logo=openai&logoColor=white)](https://www.sarvam.ai)

Production-ready Python Flask backend for **HealthCurve Nova AI**, built for the HACKHAZARDS '26 hackathon. This API serves as the central orchestration layer—connecting the frontend client to Sarvam AI Document Intelligence, Neo4j Graph Database, and LangChain-managed Gemini models for structured medical tracking.


## 🛠️ Tech Stack
* **Framework:** Python & Flask
* **Security:** Flask-CORS (Cross-Origin Resource Sharing)
* **Vision & OCR:** Sarvam AI Python SDK (`document_intelligence` Job API)
* **Graph Database:** Neo4j (GraphDatabase Driver)
* **LLM Orchestration:** LangChain (`langchain-google-genai` & `langchain-core`)
* **AI Model:** Google Gemini 2.5 Flash
* **Production Server:** Gunicorn

## ⚙️ Core Architecture
1. **Prescription Digitization (Sarvam AI):** Receives uploaded prescription files (images/PDFs) from the frontend client and creates a layout-aware Document Intelligence job to extract localized medical text.
2. **Entity Extraction (LangChain + Gemini):** Parses the raw OCR text through a structured LangChain prompt to output a predictable JSON array of medication names, exact dosages, times, and instructions.
3. **Graph Database Storage (Neo4j):** Persists the structured medication timetable into a Neo4j graph database, mapping Patient, Medicine, and TimeSlot nodes for persistent tracking.
4. **Contextual Chat Assistant (Gemini + Neo4j):** Provides an interactive chat endpoint. When asked a query, it dynamically fetches the patient's active medication timetable from Neo4j and injects it as context into the Gemini model prompt to answer queries contextually.

## 🚀 Quick Start & Installation

1. **Clone the project repository:**
   ```bash
   git clone https://github.com/AmanCodeLogs/HC-Nova-AI.git
   cd HC-Nova-AI
   ```

2. **Configure your environment keys (.env):**
   Create a `.env` file in the root directory:
   ```env
   SARVAM_API_KEY="your_sarvam_api_key"
   GEMINI_API_KEY="your_gemini_api_key"
   NEO4J_URI="neo4j+s://your-neo4j-db-uri"
   NEO4J_USERNAME="neo4j"
   NEO4J_PASSWORD="your-neo4j-password"
   ```

3. **Launch the API locally:**
   ```bash
   python app.py
   ```

## 🌐 Endpoints

### 📋 Process Prescription
* **URL:** `/api/ocr/process`
* **Method:** `POST`
* **Payload:** `multipart/form-data` with an image/pdf file attached to the `prescription` key.
* **Returns:** A JSON array containing structured medication cards:
  ```json
  {
    "timetable": [
      {
        "medicine": "Amoxicillin 500mg",
        "dosage": "1 Capsule",
        "time": "08:00 AM",
        "instructions": "After breakfast",
        "taken": false
      }
    ]
  }
  ```

### 💬 Patient Chat Consultation
* **URL:** `/api/chat`
* **Method:** `POST`
* **Payload:** `application/json` mapping `{ "message": "Your question here" }`
* **Returns:** Dynamic AI response utilizing patient medication schedule context:
  ```json
  {
    "text": "Nova AI response string"
  }
  ```


## 🌐 Live Deployments
* **Backend API (Render):** [https://hc-nova-ai.onrender.com](https://hc-nova-ai.onrender.com)
* **Frontend Web App (Netlify):** [https://hc-nova-ai.netlify.app/](https://hc-nova-ainetlify.app/)

## ☁️ Deployment Instructions

### Deployed Backend (Render)
1. Set up a new **Web Service** on Render connected to your GitHub repository.
2. Select **Python** as the runtime.
3. Configure the build and start commands:
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn app:app`
4. Add the following **Environment Variables** in the Render settings panel:
   * `SARVAM_API_KEY`: Your Sarvam AI API subscription key.
   * `GEMINI_API_KEY`: Your Google Gemini API key.
   * `NEO4J_URI`: Your Neo4j AuraDB Connection URI.
   * `NEO4J_USERNAME`: Your Neo4j database username.
   * `NEO4J_PASSWORD`: Your Neo4j database password.

### Deployed Frontend (Netlify)
1. Deploy the `Frontend/` folder as a static site on Netlify.
2. Ensure the `BACKEND_URL` inside your frontend code points to your live Render URL:
   `https://hc-nova-ai.onrender.com`

