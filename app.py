
from flask import Flask, render_template, request
from pathlib import Path
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json
import numpy as np

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "sentiment"

MODEL_PATH = MODEL_DIR / "sentiment_model.keras"
TOKENIZER_PATH = MODEL_DIR / "tokenizer.json"
CONFIG_PATH = MODEL_DIR / "config.json"

# Load the trained model and tokenizer
model = None
tokenizer = None
max_length = 20
load_error = None

try:
    model = load_model(MODEL_PATH)

    with open(TOKENIZER_PATH, "r", encoding="utf-8") as file:
        tokenizer = tokenizer_from_json(file.read())

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    max_length = config["max_length"]

except Exception as exc:
    load_error = str(exc)
    app.logger.exception("Could not load sentiment model")


def predict_sentiment(review):
    if model is None or tokenizer is None:
        raise RuntimeError("Could not load the trained model: " + str(load_error))

    sequence = tokenizer.texts_to_sequences([review])
    padded = pad_sequences(
        sequence,
        maxlen=max_length,
        padding="post",
        truncating="post"
    )

    probabilities = model.predict(padded, verbose=0)[0]
    predicted_class = int(np.argmax(probabilities))

    labels = {
        0: "Negative",
        1: "Positive",
        2: "Neutral"
    }

    prediction = labels[predicted_class]
    confidence = round(float(probabilities[predicted_class]) * 100, 2)

    return prediction, confidence


@app.route("/", methods=["GET", "POST"])
def home():
    review = ""
    prediction = None
    confidence = None
    error = None

    if request.method == "POST":
        review = request.form.get("review", "").strip()

        if not review:
            error = "Please enter a review before analyzing."
        elif len(review) > 2000:
            error = "Please keep the review under 2000 characters."
        else:
            try:
                prediction, confidence = predict_sentiment(review)
            except Exception as exc:
                app.logger.exception("Sentiment prediction error")
                error = "Prediction failed: " + str(exc)

    return render_template(
        "index.html",
        review=review,
        prediction=prediction,
        confidence=confidence,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)