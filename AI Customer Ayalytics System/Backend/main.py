from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router
from data_store import processed_data

app = FastAPI(title="SME Customer Analytics API")

@app.get("/analytics")
def get_analytics():
    return processed_data

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the SME Customer Analytics Backend",
        "status": "Running Successfully"
    }