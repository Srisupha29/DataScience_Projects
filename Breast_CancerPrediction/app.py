import streamlit as st
import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, 'breast_cancer_model.pkl'))
le = joblib.load(os.path.join(BASE_DIR, 'label_encoder.pkl'))
threshold = joblib.load(os.path.join(BASE_DIR, 'threshold.pkl'))


st.set_page_config(page_title="Breast Cancer Prediction", page_icon="🎗️", layout="wide")

st.title("🎗️ Breast Cancer Prediction")
st.write("Enter tumor measurements below to predict diagnosis.")
st.warning("⚠️ This tool is for educational purposes only. Not a substitute for medical advice.")
st.info("💡 Adjust the values above and click Predict to see the result.")

st.divider()
st.subheader("Enter Tumor Measurements")

col1, col2, col3 = st.columns(3)

with col1:
    radius_mean = st.number_input("Radius Mean", min_value=0.0, value=12.0)
    perimeter_mean = st.number_input("Perimeter Mean", min_value=0.0, value=78.0)
    area_mean = st.number_input("Area Mean", min_value=0.0, value=477.0)
    compactness_mean = st.number_input("Compactness Mean", min_value=0.0, value=0.08)

with col2:
    concavity_mean = st.number_input("Concavity Mean", min_value=0.0, value=0.05)
    concave_points_mean = st.number_input("Concave Points Mean", min_value=0.0, value=0.03)
    radius_worst = st.number_input("Radius Worst", min_value=0.0, value=14.0)
    perimeter_worst = st.number_input("Perimeter Worst", min_value=0.0, value=92.0)

with col3:
    area_worst = st.number_input("Area Worst", min_value=0.0, value=600.0)
    compactness_worst = st.number_input("Compactness Worst", min_value=0.0, value=0.18)
    concavity_worst = st.number_input("Concavity Worst", min_value=0.0, value=0.17)
    concave_points_worst = st.number_input("Concave Points Worst", min_value=0.0, value=0.07)

st.divider()

if st.button("Predict", use_container_width=True):

    input_data = np.array([[
        radius_mean, perimeter_mean, area_mean, compactness_mean,
        concavity_mean, concave_points_mean, radius_worst, perimeter_worst,
        area_worst, compactness_worst, concavity_worst, concave_points_worst
    ]])

    proba = model.predict_proba(input_data)[:, 1][0]
    prediction = 1 if proba >= threshold else 0
    confidence = proba if prediction == 1 else 1 - proba

    st.write("**Malignancy Risk Level:**")
    st.progress(float(proba))

    st.divider()

    if prediction == 1:
        st.error("⚠️ Result: Malignant")
        st.metric("Malignancy Probability", f"{proba:.1%}")
    else:
        st.success("✅ Result: Benign")
        st.metric("Benign Probability", f"{1 - proba:.1%}")

    col1, col2 = st.columns(2)
    col1.metric("Malignancy Probability", f"{proba:.1%}")
    col2.metric("Confidence", f"{confidence:.1%}")
