"""FastAPI server for crowd status API.
"""

import datetime
from typing import TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class CrowdStatus(TypedDict):
    """Crowd status and timestamp.

    :param status: The crowd status
    :type status: float
    :param timestamp: The timestamp of the crowd status
    :type timestamp: datetime.datetime
    """

    status: float
    timestamp: datetime.datetime


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to a specific origin if desired)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

crowd_status = CrowdStatus(status=0.0, timestamp=datetime.datetime.fromtimestamp(0))


@app.post("/api/update_crowd_status")
def update_crowd_status(status: dict) -> None:
    """Updates the crowd status.

    :param status: The crowd status and timestamp
    :type status: dict
    """

    crowd_level = float(status["status"])
    timestamp = status["timestamp"]
    try:
        # Use ISO8601 format for timestamp: YYYY-MM-DD[T]HH:MM:SS
        timestamp = datetime.datetime.fromisoformat(timestamp)
    except TypeError as exc:
        print(f"Error: {exc}")
        timestamp = datetime.datetime.now()
    except ValueError as exc:
        print(f"Error: {exc}")
        timestamp = datetime.datetime.now()
    finally:
        crowd_status["status"] = crowd_level
        crowd_status["timestamp"] = timestamp


@app.get("/api/get_crowd_status")
def get_crowd_status() -> CrowdStatus:
    """Gets the current crowd status.

    :return: The crowd status and timestamp
    :rtype: dict[str, float | datetime.datetime]
    """
    return crowd_status
