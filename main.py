from fastapi import FastAPI
from pydantic import BaseModel
from ai_agent import AIAgentManager, DEFAULT_CONFIG

app = FastAPI()
ai_manager = AIAgentManager(DEFAULT_CONFIG)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def hello_world():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await ai_manager.run(request.message)
    return ChatResponse(response=response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)