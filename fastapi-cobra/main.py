from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gunicorn
from pydantic import BaseModel
from model import predict, predict_helper
import numpy as np

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pydantic models


class request_body(BaseModel):
    employ: str
    age: int
    amount: int
    duration: int
    checkingstatus: str
    history: str
    purpose: str
    savings: str
    status: str


@app.get("/")
def welcome():
    return {"ping": "Hello COBRA. Go to /docs to see the Swagger documentation"}


@app.post("/predict", status_code=200)
def get_prediction(data: request_body):
    print(data)

    prediction_json = predict_helper(
        data.employ,
        data.age,
        data.amount,
        data.duration,
        data.checkingstatus,
        data.history,
        data.purpose,
        data.savings,
        data.status,
    )

    if not prediction_json:
        raise HTTPException(status_code=400, detail="Model not found.")

    return prediction_json
