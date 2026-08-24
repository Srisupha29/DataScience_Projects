const form = document.getElementById("prediction-form");

const results = document.getElementById("results");
const errorMessage = document.getElementById("error-message");

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    results.classList.add("hidden");
    errorMessage.classList.add("hidden");

    const shipment = {
        month: document.getElementById("month").value,
        product: document.getElementById("product").value,
        province_origin: document.getElementById("province_origin").value,
        province_destination: document.getElementById("province_destination").value,
        average_distance: Number(
            document.getElementById("average_distance").value
        ),
        trips: Number(
            document.getElementById("trips").value
        ),
        shipping: Number(
            document.getElementById("shipping").value
        )
    };

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/predict",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(shipment)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail
                    ? JSON.stringify(data.detail)
                    : "Prediction failed."
            );
        }

        document.getElementById("predicted-duration").textContent =
            `${data.predicted_duration.toFixed(2)} days`;

        document.getElementById("delay-probability").textContent =
            `${(data.delay_probability * 100).toFixed(2)}%`;

        document.getElementById("delay-prediction").textContent =
            data.delay_prediction;

        document.getElementById("risk-score").textContent =
            `${data.risk_score.toFixed(2)}`;

        document.getElementById("risk-category").textContent =
            data.risk_category;

        results.classList.remove("hidden");

    } catch (error) {

        console.error(error);

        errorMessage.textContent =
            `Error: ${error.message}`;

        errorMessage.classList.remove("hidden");
    }

});