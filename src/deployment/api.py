"""FastAPI server for crowd status API.
"""

import datetime
from typing import TypedDict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deployment.config import UVICORN_HOST


class CrowdStatus(TypedDict):
    """Crowd status and timestamp.

    :param status: The crowd status
    :type status: float
    :param timestamp: The timestamp of the crowd status
    :type timestamp: datetime.datetime
    """

    status: float
    one_sigma_conf_interval: float | None
    timestamp: datetime.datetime


app = FastAPI(
    title="Crowd Status API",
    description="API for updating and retrieving the crowd status",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to a specific origin if desired)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

crowd_status = CrowdStatus(
    status=0.0,
    one_sigma_conf_interval=None,
    timestamp=datetime.datetime.fromtimestamp(0),
)


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

    if "err" in status:
        crowd_status["one_sigma_conf_interval"] = status["err"]


@app.get("/api/get_crowd_status")
def get_crowd_status() -> dict:
    """Gets the current crowd status.

    :return: The crowd status and timestamp
    :rtype: CrowdStatus
    """
    if crowd_status["one_sigma_conf_interval"] is not None:
        return dict(crowd_status)
    return {k: v for k, v in crowd_status.items() if k != "one_sigma_conf_interval"}


if __name__ == "__main__":
    uvicorn.run(app, host=UVICORN_HOST, port=8000, log_level="info")
