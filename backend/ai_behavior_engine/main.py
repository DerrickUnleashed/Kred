from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_behavior_engine.routes import router as ai_behavior_router

app = FastAPI(title="AI Behavior Engine (Dev Mode)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_behavior_router)


@app.get("/")
def root():
    return {"message": "AI Behavior Engine running 🚀"}