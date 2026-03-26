import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaskRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"status": "AI Hackathon Starter Kit Online"}

@app.post("/process")
def process_text(request: TaskRequest):
    # This is a placeholder for your LLM call (OpenAI, Anthropic, or Local)
    # response = llm.invoke(request.text)
    processed_text = request.text.upper()  # Generic "AI" processing
    return {
        "original": request.text,
        "processed": processed_text,
        "message": "Update this endpoint to call your LLM of choice!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
