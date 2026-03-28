from fastapi import FastAPI
from .router import router as dynamic_router

app = FastAPI(
    title="Dynamic Spending Limit Engine (Test)",
    version="1.0"
)

app.include_router(dynamic_router)


@app.get("/")
def root():
    return {"message": "Dynamic Limit Engine running"}