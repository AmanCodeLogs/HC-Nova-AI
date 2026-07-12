import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# AI and Graph Database Drivers
from sarvamai import SarvamAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from neo4j import GraphDatabase

app = Flask(__name__)
CORS(app)

# Credentials
SARVAM_KEY = os.environ.get("SARVAM_API_KEY", "MISSING")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "MISSING")
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USERNAME", "neo4j") 
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# Initialize Clients
try:
    sarvam_client = SarvamAI(api_subscription_key=SARVAM_KEY) if SARVAM_KEY != "MISSING" else None
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_KEY) if GEMINI_KEY != "MISSING" else None
    
    # Establish Neo4j Driver Connection
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
except Exception as e:
    print(f"Initialization Error: {e}")
    sarvam_client, llm, neo4j_driver = None, None, None

def save_to_neo4j(timetable):
    """Saves the extracted medications into Neo4j graph nodes and links them."""
    if not neo4j_driver:
        return
    
    query = """
    MERGE (p:Patient {id: "CurrentPatient"})
    WITH p
    UNWIND $timetable AS item
    MERGE (m:Medicine {name: item.medicine})
    SET m.dosage = item.dosage, m.instructions = item.instructions
    MERGE (t:TimeSlot {time: item.time})
    MERGE (p)-[:TAKES]->(m)
    MERGE (m)-[:SCHEDULED_AT]->(t)
    """
    try:
        with neo4j_driver.session() as session:
            session.run(query, timetable=timetable)
            print("Successfully saved nodes to Neo4j!")
    except Exception as e:
        print(f"Neo4j Transaction Error: {e}")

@app.route('/api/ocr/process', methods=['POST'])
def process_prescription():
    fallback_timetable = [
        { "medicine": "Amoxicillin 500mg", "dosage": "1 Capsule", "time": "08:00 AM", "instructions": "After breakfast", "taken": False }
    ]

    if 'prescription' not in request.files:
        return jsonify({"timetable": fallback_timetable}), 200
        
    file = request.files['prescription']
    if not sarvam_client or not llm:
        # Even in fallback mode, try to save the demo data to Neo4j if database is up
        save_to_neo4j(fallback_timetable)
        return jsonify({"timetable": fallback_timetable}), 200

    try:
        temp_path = f"/tmp/{file.filename}"
        file.save(temp_path)
        
        vision_response = sarvam_client.document_digitization.digitize(file_path=temp_path, language="en-IN", output_format="md")
        
        extraction_prompt = PromptTemplate.from_template("""
        Extract medication details from this text into a raw JSON array format only:
        [ {{"medicine": "Name", "dosage": "1 tab", "time": "08:00 AM", "instructions": "After food", "taken": false}} ]
        Text: {raw_text}
        """)
        
        chain = extraction_prompt | llm
        llm_result = chain.invoke({"raw_text": str(vision_response)})
        clean_json = llm_result.content.replace("```json", "").replace("```", "").strip()
        timetable_data = json.loads(clean_json)
        
        # Save to database before returning response to client
        save_to_neo4j(timetable_data)
        
        return jsonify({"timetable": timetable_data})
    except Exception as e:
        save_to_neo4j(fallback_timetable)
        return jsonify({"timetable": fallback_timetable}), 200

@app.route('/api/chat', methods=['POST'])
def chat_consultation():
    data = request.get_json() or {}
    user_message = data.get('message', '')

    if not llm:
        return jsonify({"text": "Error: Gemini AI is not initialized. Check your API keys."})

    try:
        # Prompting Gemini to act as the HealthCurve Assistant
        prompt = f"You are Nova AI, a helpful medical assistant for the HealthCurve app. Answer this health query safely and concisely: {user_message}"
        response = llm.invoke(prompt)

        return jsonify({"text": response.content})
    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"text": "Sorry, I am having trouble connecting to my brain right now!"})
