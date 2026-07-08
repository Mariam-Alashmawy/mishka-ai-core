from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from modules.file_processor import FileProcessor
from modules.generator import Generator
from modules.memory_manager import MemoryManager
import shutil
import os
from typing import Optional 

app = FastAPI(title="Mishka AI Study Partner")

@app.get("/")
async def root():
    return {"message": "Welcome to Mishka AI Study Partner! Go to /docs to test the API."}

# Initialize Modules
processor = FileProcessor()
ai_engine = Generator()
session_manager = MemoryManager()

# Ensure upload directory exists
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    summary_level: str = Form("detailed") # Options: 'simple' or 'detailed'
):
    # 1. Save the file locally
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # 2. Create a Session
    session_id = session_manager.create_new_session(file_location)

    # 3. Extract Content
    content_data = processor.extract_content(file_location, file.content_type)
    
    if "error" in content_data:
        os.remove(file_location) 
        raise HTTPException(status_code=400, detail=content_data['error'])

    # 4. Save content data for later tool generation
    session_manager.save_input_context(session_id, content_data)

    # 5. Generate Initial Explanation
    explanation = ai_engine.generate_explanation(content_data, summary_level)

    # 6. Update History
    session_manager.add_turn(
        session_id,
        f"Explain this file. Level: {summary_level}",
        explanation
    )

    return {
        "session_id": session_id,
        "explanation": explanation
    }

@app.post("/chat")
async def chat(session_id: str, message: str):
    session = session_manager.get_session_data(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = session["history"]
    response_text = ai_engine.chat(history, message)
    session_manager.add_turn(session_id, message, response_text)
    
    return {"response": response_text}

@app.post("/generate-tools")
async def generate_study_tools(
    session_id: str,
    tool_type: str, 
    complexity: str = "Intermediate" 
):
    session = session_manager.get_session_data(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get the raw content data we saved during upload
    content_data = session.get("input_context")
    if not content_data:
        raise HTTPException(status_code=400, detail="No study material found for this session.")

    result = ai_engine.generate_tool_directly(
        tool_type=tool_type.lower(),
        complexity=complexity,
        content_data=content_data
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result