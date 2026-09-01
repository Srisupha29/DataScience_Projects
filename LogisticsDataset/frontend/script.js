const form = document.getElementById("predictionForm");

const results = document.getElementById("results");
const routeComparison = document.getElementById("routeComparison");
const recommendation = document.getElementById("recommendation");
const errorMessage = document.getElementById("errorMessage");

const routeTableBody = document.getElementById("routeTableBody");


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    // Hide previous results
    results.classList.add("hidden");
    routeComparison.classList.add("hidden");
    recommendation.classList.add("hidden");
    errorMessage.classList.add("hidden");



    const shipmentData = {

        month: document.getElementById("month").value,

        product: document.getElementById("product").value,

        province_origin:
            document.getElementById("origin").value,

        province_destination:
            document.getElementById("destination").value,

        trips:
            Number(document.getElementById("trips").value),

        shipping:
            Number(document.getElementById("shipping").value)

    };


    try {


        const response = await fetch(
            "http://127.0.0.1:8000/predict",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(shipmentData)
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                    ? JSON.stringify(data.detail)
                    : "Prediction request failed."
            );

        }


        document.getElementById("predictedDuration").textContent =
            `${Number(data.predicted_duration).toFixed(2)} days`;


        document.getElementById("delayProbability").textContent =
            `${(Number(data.delay_probability) * 100).toFixed(2)}%`;


        document.getElementById("delayPrediction").textContent =
            data.delay_prediction;


        document.getElementById("riskScore").textContent =
            `${Number(data.risk_score).toFixed(2)}`;


        document.getElementById("riskCategory").textContent =
            data.risk_category;


        results.classList.remove("hidden");



        const routes = [

            {
                route: "Route A",
                distance: "520 km",
                traffic: "High",
                weather: "Clear",
                duration: "680 min",
                risk: "High"
            },

            {
                route: "Route B",
                distance: "545 km",
                traffic: "Low",
                weather: "Clear",
                duration: "620 min",
                risk: "Medium"
            },

            {
                route: "Route C",
                distance: "560 km",
                traffic: "Medium",
                weather: "Rain",
                duration: "700 min",
                risk: "High"
            }

        ];

        routeTableBody.innerHTML = "";


        routes.forEach(function (route) {

            const row = document.createElement("tr");

            row.innerHTML = `

                <td>${route.route}</td>

                <td>${route.distance}</td>

                <td>${route.traffic}</td>

                <td>${route.weather}</td>

                <td>${route.duration}</td>

                <td>${route.risk}</td>

            `;

            routeTableBody.appendChild(row);

        });


        routeComparison.classList.remove("hidden");

        document.getElementById("recommendedRoute").textContent =
            "Route B";


        document.getElementById("recommendationReason").textContent =
            "Route B currently provides the lowest predicted duration and lower delay risk among the available routes. Traffic and weather conditions will be incorporated once the external APIs are connected.";


        recommendation.classList.remove("hidden");

    }


    catch (error) {

        errorMessage.textContent =
            `Error: ${error.message}`;

        errorMessage.classList.remove("hidden");

    }

});