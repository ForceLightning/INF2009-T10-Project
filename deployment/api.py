import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to a specific origin if desired)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

crowd_status = None
last_updated_time = None

@app.post("/api/update_crowd_status")
def update_crowd_status(status: dict):
    global crowd_status, last_updated_time

    crowd_status = status["status"]
    last_updated_time = status["timestamp"]

@app.get("/api/get_crowd_status")
def get_crowd_status():
    return {"crowd_status": crowd_status, "timestamp": last_updated_time}