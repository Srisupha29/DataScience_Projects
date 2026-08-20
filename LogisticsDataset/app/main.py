from fastapi import FastAPI
from app.schemas import ShipmentInput, PredictionResponse
from app.predictor import predict_shipment


app = FastAPI(
    title="Thai Logistics Prediction API",
    description="API for shipment duration, delay prediction, and logistics risk scoring.",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Thai Logistics Prediction API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(shipment: ShipmentInput):

    result = predict_shipment(
        month=shipment.month,
        product=shipment.product,
        province_origin=shipment.province_origin,
        province_destination=shipment.province_destination,
        average_distance=shipment.average_distance,
        trips=shipment.trips,
        shipping=shipment.shipping
    )

    return result