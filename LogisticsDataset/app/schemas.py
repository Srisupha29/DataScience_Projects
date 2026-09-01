from pydantic import BaseModel, Field


class ShipmentInput(BaseModel):
    month: str
    product: str
    province_origin: str
    province_destination: str

    trips: int = Field(gt=0)
    shipping: float = Field(gt=0)


class PredictionResponse(BaseModel):
    predicted_duration: float
    delay_probability: float
    delay_prediction: str
    risk_score: float
    risk_category: str