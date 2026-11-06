
from flask import Flask, request, jsonify
import joblib
import os

# =====================================
# 1. INITIALIZE FLASK
# =====================================

app = Flask(__name__)

# =====================================
# 2. LOAD TRAINED ML MODEL
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "spam_model.pkl"
)

model = joblib.load(MODEL_PATH)

print("SpamShield AI model loaded successfully!")


# =====================================
# 3. HOME ROUTE
# =====================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "project": "SpamShield AI",
        "description": "Intelligent SMS Spam Detection API",
        "status": "Running",
        "model": "Linear SVM",
        "version": "1.0"
    })


# =====================================
# 4. HEALTH CHECK
# =====================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "model_name": "Linear SVM"
    })


# =====================================
# 5. SINGLE SMS PREDICTION
# =====================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # Get JSON request
        data = request.get_json(silent=True)

        # Validate JSON
        if not isinstance(data, dict):
            return jsonify({
                "error": "Request must contain valid JSON"
            }), 400

        # Extract message
        message = data.get("message")

        # Validate message
        if not isinstance(message, str) or not message.strip():

            return jsonify({
                "error": "Please provide a valid SMS message"
            }), 400

        # Apply trained model
        prediction = int(model.predict([message])[0])

        # Get probabilities
        probabilities = model.predict_proba([message])[0]

        spam_probability = float(probabilities[1]) * 100
        ham_probability = float(probabilities[0]) * 100

        # Convert numerical prediction
        result = "SPAM" if prediction == 1 else "HAM"

        # Return response
        return jsonify({

            "success": True,

            "message": message,

            "prediction": result,

            "spam_probability": round(
                spam_probability, 2
            ),

            "ham_probability": round(
                ham_probability, 2
            ),

            "model": "Linear SVM"

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================
# 6. BATCH SMS PREDICTION
# =====================================

@app.route("/predict/batch", methods=["POST"])
def batch_predict():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error": "Invalid JSON request"
            }), 400

        messages = data.get("messages")

        if not isinstance(messages, list) or not messages:

            return jsonify({
                "error": "Please provide a non-empty messages list"
            }), 400

        if len(messages) > 500:

            return jsonify({
                "error": "Maximum 500 messages allowed"
            }), 400

        if not all(
            isinstance(message, str) and message.strip()
            for message in messages
        ):

            return jsonify({
                "error": "All messages must be non-empty strings"
            }), 400

        # Predict all messages together
        predictions = model.predict(messages)

        probabilities = model.predict_proba(messages)

        results = []

        for message, prediction, probability in zip(
            messages, predictions, probabilities
        ):

            results.append({

                "message": message,

                "prediction": (
                    "SPAM" if int(prediction) == 1 else "HAM"
                ),

                "spam_probability": round(
                    float(probability[1]) * 100, 2
                ),

                "ham_probability": round(
                    float(probability[0]) * 100, 2
                )

            })

        return jsonify({

            "success": True,

            "total_messages": len(results),

            "results": results

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =====================================
# 7. RUN FLASK SERVER
# =====================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
