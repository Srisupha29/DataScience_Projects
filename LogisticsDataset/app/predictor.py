import joblib
import pandas as pd
from huggingface_hub import hf_hub_download

# Load trained models and preprocessing

duration_model_path = hf_hub_download(
    repo_id="SrisuphaChawla/Logistics-Model",
    filename="duration_model.pkl"
)

duration_model = joblib.load(
    duration_model_path
)

duration_preprocessor = joblib.load(
    "models/duration_preprocessor.pkl"
)

delay_model = joblib.load(
    "models/delay_model.pkl"
)

delay_preprocessor = joblib.load(
    "models/delay_preprocessor.pkl"
)

delay_threshold = joblib.load(
    "models/delay_threshold.pkl"
)

risk_config = joblib.load(
    "models/risk_config.pkl"
)

# Prediction function

def predict_shipment(
    month,
    product,
    province_origin,
    province_destination,
    average_distance,
    trips,
    shipping
):
    # Create input DataFrame

    input_data = pd.DataFrame([{
        "month": month,
        "product": product,
        "province_origin": province_origin,
        "province_destination": province_destination,
        "average_distance": average_distance,
        "trips": trips,
        "shipping": shipping
    }])

    # 1. Shipping Duration Prediction

    duration_encoded = duration_preprocessor.transform(
        input_data
    )

    predicted_duration = duration_model.predict(
        duration_encoded
    )[0]

    # 2. Delay Prediction

    delay_encoded = delay_preprocessor.transform(
        input_data
    )

    delay_probability = delay_model.predict_proba(
        delay_encoded
    )[0, 1]

    # 3. Apply Final Threshold

    delay_prediction = (
        "Delayed"
        if delay_probability >= delay_threshold
        else "Not Delayed"
    )

    # 4. Risk Score

    risk_score = delay_probability * 100

    # 5. Risk Category

    if risk_score < 30:

        risk_category = "Low"

    elif risk_score < 60:

        risk_category = "Medium"

    else:

        risk_category = "High"

    # Return Results

    return {
        "predicted_duration": float(predicted_duration),
        "delay_probability": float(delay_probability),
        "delay_prediction": delay_prediction,
        "risk_score": float(risk_score),
        "risk_category": risk_category
    }