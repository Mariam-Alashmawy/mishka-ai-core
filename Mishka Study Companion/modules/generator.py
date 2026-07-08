import os
import json
import re 
from openai import OpenAI  
from PIL import Image
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from .memory_manager import MemoryManager 
import httpx

# Load environment variables
load_dotenv()

class Generator:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("⚠️ WARNING: OPENROUTER_API_KEY is missing or None. Check your .env file path.")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=60.0,  
            max_retries=3
        )
        self.model_name = "google/gemini-2.5-flash" 
        self.session_manager = MemoryManager()

    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Handles the API call via OpenRouter's OpenAI-compatible endpoint with fallback safety."""
        if not self.client.api_key:
            return "ERROR: OpenRouter API key not found. Check your .env setup."
            
        try:
            # to pass custom OpenRouter routing limits safely through the OpenAI SDK wrapper.
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=4000,
                extra_headers={
                    "HTTP-Referer": "https://mishka-ai-tutor.com", 
                    "X-Title": "Mishka AI Tutor",
                    # 🛡️ FORCES OpenRouter to fail instead of falling back to expensive models
                    "openrouter_route": "fallback" 
                },
                # 🚫 Lock OpenRouter down so it ONLY queries this specific array
                extra_body={
                    "models": [self.model_name]
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenRouter API Error: {str(e)}"

    def generate_explanation(self, content_data: Dict[str, Any], summary_level: str) -> str:
        level_instruction = "Explain in deep detail." if summary_level != "simple" else "Explain simply for beginners."
        study_material = content_data.get('content', '')
        
        prompt = f"You are Mishka, an AI Tutor. {level_instruction}\n\nMaterial: {study_material}"
        messages = [{"role": "user", "content": prompt}]
        return self._call_api(messages)

    def chat(self, history: List[Dict[str, Any]], new_question: str) -> str:
        """Handles chat using OpenRouter (OpenAI format)."""
        formatted_messages = []
        
        for turn in history:
            role = 'assistant' if turn['role'] in ['assistant', 'model'] else 'user'
            if 'parts' in turn:
                text = turn['parts'][0]['text'] if isinstance(turn['parts'][0], dict) else turn['parts'][0]
            else:
                text = turn.get('content', '')
            
            formatted_messages.append({"role": role, "content": text})
            
        # Append the new user question
        formatted_messages.append({"role": "user", "content": new_question})
        return self._call_api(formatted_messages)
    
    def generate_tool_directly(self, tool_type: str, complexity: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        study_material = content_data.get('content', '')
        json_schema_prompt = ""
        json_structure = ""
        complexity_instruction = ""

        if tool_type == 'quizzes':
            json_schema_prompt = "Generate 10 unique Multiple Choice Questions (MCQs) based on the material."
            json_structure = """
            [
                {
                    "question": "MCQ question text.",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "The correct option text."
                }
            ]
            """
            complexity_instruction = f"Difficulty Level: {complexity}. Ensure distractors are highly plausible."
        
        elif tool_type == 'flashcards':
            json_schema_prompt = "Generate 10 diverse flashcards from the material. The content on the 'front' must be a mix of Key Terms, Key Facts, and Important Notes."
            json_structure = """
            [
                {
                    "type": "The content type of the card's front side. MUST be one of: 'term', 'fact', or 'note'.",
                    "front": "The short text of the Term, Fact, or Note.",
                    "back": "The definition, explanation, or context of the text on the 'front'."
                }
            ]
            """
            complexity_instruction = "Ensure the 10 cards contain an even mix of 'term', 'fact', and 'note' types."
        
        elif tool_type == 'mind_maps':
            json_schema_prompt = "TASK: Analyze the material and structure it into a hierarchical Mind Map JSON."
            json_structure = """
            {
              "title": "Core Lecture Topic",
              "children": [
                {
                  "title": "Main Sub-Heading Pillar",
                  "children": [
                    {"title": "Detailed supporting fact or sub-point", "children": []}
                  ]
                }
              ]
            }
            """
            complexity_instruction = "CRITICAL: Ensure your output is perfectly structured JSON. Maintain a deep, valid 3-level parent-child hierarchy with matching brackets. Do not leave empty strings or hanging commas. Ensure a logical grouping with a strict maximum of 3 levels of depth. Keep the 'title' string inside nodes brief (under 10 words per point) to ensure a clean visual tree."
        
        else:
            return {"status": "error", "message": f"Tool type '{tool_type}' not supported."}

        if not study_material:
            return {"status": "error", "message": "Document content is empty."}

        full_prompt = f"""
        {json_schema_prompt}
        {complexity_instruction}
        RETURN ONLY THE JSON. NO MARKDOWN. NO TEXT.
        Structure: {json_structure}
        Study Material: {study_material}
        """
        
        # Call API with temperature 0 for JSON stability
        raw_json_string = self._call_api([{"role": "user", "content": full_prompt}], temperature=0.0)
        
        # ROBUST CLEANING LOGIC
        # NEW ROBUST CLEANING PIPELINE:
        try:
            clean_json = raw_json_string.strip()
            
            # 1. Strip away markdown code block wrappers if they exist
            clean_json = re.sub(r'^```json\s*', '', clean_json, flags=re.IGNORECASE)
            clean_json = re.sub(r'^```\s*', '', clean_json, flags=re.IGNORECASE)
            clean_json = re.sub(r'\s*```$', '', clean_json)
            clean_json = clean_json.strip()
            
            # 2. Use regex to extract the absolute inner JSON boundaries
            if tool_type == 'mind_maps':
                match = re.search(r'(\{[\s\S]*\})', clean_json)
            else:
                match = re.search(r'(\[[\s\S]*\])', clean_json)
                
            if match:
                clean_json = match.group(1).strip()
            
            # 3. Clean up catastrophic trailing commas inside nested dictionary elements
            # (e.g., {"title": "X", "children": [],} -> {"title": "X", "children": []})
            clean_json = re.sub(r',\s*([\]}])', r'\1', clean_json)
            
            parsed_content = json.loads(clean_json)
            return {"status": "success", "tool_type": tool_type, "content": parsed_content}
            
        except json.JSONDecodeError as e:
            print(f"--- PARSING FAILURE DEBUG LOG ---")
            print(f"Raw Model Output:\n{raw_json_string}")
            print(f"Cleaned Output Tried:\n{clean_json}")
            print(f"Decode Error Detail: {e}")
            return {"status": "error", "message": f"Failed to parse API output into JSON. Structural syntax error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected parsing error: {e}"}
            
        except json.JSONDecodeError as e:
            print(f"Decode Error: {e}")
            return {"status": "error", "message": "Failed to parse API output into JSON."}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    def generate_json_summary(self, history: List[Dict[str, Any]]) -> str:
        """
        Analyzes the full conversation history and builds a structured,
        comprehensive JSON summary report for the student's study session.
        """
        formatted_messages = []
        
        # Format the existing chat log history for the API payload
        for turn in history:
            role = 'assistant' if turn['role'] in ['assistant', 'model'] else 'user'
            if 'parts' in turn:
                text = turn['parts'][0]['text'] if isinstance(turn['parts'][0], dict) else turn['parts'][0]
            else:
                text = turn.get('content', '')
            formatted_messages.append({"role": role, "content": text})

        # Define a structured schema prompt for stable compilation
        summary_prompt = """
        TASK: Analyze the entire preceding conversation history between the student and the AI tutor.
        Generate a comprehensive session study report structured exactly as a flat JSON block.
        
        DO NOT include any Markdown formatting blocks (no ```json, no ```). RETURN ONLY THE RAW JSON STRING.
        
        Expected JSON Structure:
        {
            "topic": "The main educational subject or topic discussed during this session.",
            "difficulty_level": "An assessment of the material complexity (e.g., Beginner, Intermediate, Advanced).",
            "summary": "A deep, comprehensive paragraph summarizing the core academic concepts reviewed.",
            "key_points": [
                "Key takeaway point 1 from the conversation.",
                "Key takeaway point 2 from the conversation.",
                "Key takeaway point 3 from the conversation."
            ],
            "student_questions": [
                "List of main questions or doubts the student explicitly raised during the chat context."
            ]
        }
        """
        
        # Append the final compiler prompt instruction
        formatted_messages.append({"role": "user", "content": summary_prompt})
        
        # Call the model with low temperature for syntax stability
        return self._call_api(formatted_messages, temperature=0.2)