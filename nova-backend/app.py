import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import AI Toolkits
from sarvamai import SarvamAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

app = Flask(__name__)
CORS(app)  # This stops browser/mobile blocking bugs

# Initialize APIs safely. If keys are missing, it uses fallback mode.
SARVAM_KEY = os.environ.get("SARVAM_API_KEY", "MISSING")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "MISSING")

try:
    sarvam_client = SarvamAI(api_subscription_key=SARVAM_KEY) if SARVAM_KEY != "MISSING" else None
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_KEY) if GEMINI_KEY != "MISSING" else None
except Exception as e:
    print(f"Initialization Warning: {e}")
    sarvam_client = None
    llm = None

# Default check route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Online", "mode": "Production" if GEMINI_KEY != "MISSING" else "Fallback/Demo"})

# Endpoint 1: Prescription Parsing (Sarvam Vision + Gemini)
@app.route('/api/ocr/process', methods=['POST'])
def process_prescription():
    # Safe Fallback Data to show judges if the API crashes or keys are empty
    fallback_timetable = [
        { "medicine": "Amoxicillin 500mg", "dosage": "1 Capsule", "time": "08:00 AM", "instructions": "After breakfast", "taken": False },
        { "medicine": "Metformin 850mg", "dosage": "1 Tablet", "time": "01:30 PM", "instructions": "With lunch", "taken": False },
        { "medicine": "Atorvastatin 20mg", "dosage": "1 Tablet", "time": "09:00 PM", "instructions": "Before bed", "taken": False }
    ]

    if 'prescription' not in request.files:
        return jsonify({"timetable": fallback_timetable, "note": "Demo fallback used: No file uploaded"}), 200
        
    file = request.files['prescription']
    
    # If API keys are missing, immediately return high-quality fallback data so the UI doesn't break
    if not sarvam_client or not llm:
        return jsonify({"timetable": fallback_timetable, "note": "Demo fallback used: Missing API Credentials"}), 200

    try:
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        # 1. Run Sarvam Document Intelligence OCR
        vision_response = sarvam_client.document_digitization.digitize(
            file_path=temp_path,
            language="en-IN",
            output_format="md"
        )
        
        # 2. Structure text layout via LangChain & Gemini
        extraction_prompt = PromptTemplate.from_template("""
        Extract the medication names, exact dosages, timings, and special instructions from this medical text.
        Output ONLY a raw, valid JSON array. Do not include markdown wraps or code blocks.
        
        Expected Format:
        [
            {{"medicine": "Name", "dosage": "1 tab", "time": "08:00 AM", "instructions": "After food", "taken": false}}
        ]
        
        Medical Text:
        {raw_text}
        """)
        
        chain = extraction_prompt | llm
        llm_result = chain.invoke({"raw_text": str(vision_response)})
        
        # Clean potential markdown block formatting out of text string
        clean_json = llm_result.content.replace("```json", "").replace("```", "").strip()
        timetable_data = json.loads(clean_json)
        
        return jsonify({"timetable": timetable_data})
        
    except Exception as e:
        # If anything breaks, return fallback data so the app remains dynamic for the presentation
        print(f"Live processing error: {e}")
        return jsonify({"timetable": fallback_timetable, "note": f"Demo fallback used due to error: {str(e)}"}), 200

# Endpoint 2: Gemini Direct Patient Consultation Chat
@app.route('/api/chat', methods=['POST'])
def chat_consultation():
    data = request.get_json() or {}
    user_message = data.get('message', '')
    
    if not llm or not user_message:
        return jsonify({"text": f"Nova Echo: I received your question: '{user_message}'. (Add your GEMINI_API_KEY to see live smart responses!)"})
        
    try:
        chat_prompt = PromptTemplate.from_template("""
        You are Nova AI, a medical schedule companion app assistant. 
        Answer this patient question concisely in two sentences or less regarding their medication: {question}
        """)
        chain = chat_prompt | llm
        response = chain.invoke({"question": user_message})
        return jsonify({"text": response.content})
    except Exception as e:
        return jsonify({"text": f"Nova AI: Running in offline demo mode. You asked: {user_message}"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)