"""FastAPI server for crowd status API.
"""

import datetime

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

# TODO: Use a TypedDict for the status parameter.
CROWD_STATUS: float | None = None
LAST_UPDATED_TIME: datetime.datetime | None = None


@app.post("/api/update_crowd_status")
def update_crowd_status(status: dict) -> None:
    """Updates the crowd status.

    :param status: The crowd status and timestamp
    :type status: dict
    """
    global CROWD_STATUS, LAST_UPDATED_TIME

    CROWD_STATUS = status["status"]
    LAST_UPDATED_TIME = status["timestamp"]


@app.get("/api/get_crowd_status")
def get_crowd_status() -> dict:
    """Gets the current crowd status.

    :return: The crowd status and timestamp
    :rtype: dict[str, float | datetime.datetime]
    """
    return {"crowd_status": CROWD_STATUS, "timestamp": LAST_UPDATED_TIME}
