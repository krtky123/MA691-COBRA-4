from fastapi import FastAPI
import uvicorn
import gunicorn
from pydantic import BaseModel
from model import predict, convert
import numpy as np

app = FastAPI()

# pydantic models


class request_body(BaseModel):
    Pclass: int
    Sex: int
    SibSp: int
    Parch: int
    Embarked: int
    AgeGroup: int
    Title: int
    FareBand: int


@app.get("/")
def welcome():
    return {"ping": "Hello COBRA"}


@app.post("/predict", status_code=200)
def get_prediction(data: request_body):
    print(data)
    feature_vector = np.array([[data.Pclass, data.Sex, data.SibSp, data.Parch,
                              data.Embarked, data.AgeGroup, data.Title, data.FareBand]])
    prediction_list = predict(feature_vector)

    if not prediction_list:
        raise HTTPException(status_code=400, detail="Model not found.")

    response_object = convert(prediction_list)
    return response_object
