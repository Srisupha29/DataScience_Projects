from fastapi import FastAPI
from app.schemas import ShipmentInput, PredictionResponse
from app.predictor import predict_shipment
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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