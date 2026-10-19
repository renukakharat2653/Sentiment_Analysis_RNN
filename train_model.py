
from pathlib import Path
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "sentiment"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Small starter dataset for demonstrating sentiment analysis
texts = [
    "I love this movie", "This movie is fantastic",
    "Amazing story and great acting", "I really enjoyed it",
    "Excellent product", "Very happy with this purchase",
    "The film was wonderful", "Absolutely brilliant",
    "I liked it a lot", "Great experience",
    "This is a good movie", "The product works perfectly",
    "I hate this movie", "This movie is terrible",
    "Awful story and bad acting", "I really disliked it",
    "Worst product ever", "Very disappointed with this purchase",
    "The film was boring", "Absolutely horrible",
    "I did not enjoy it", "Terrible experience",
    "This is a bad movie", "The product stopped working",
    "It was okay", "Nothing special",
    "The movie was average", "The product is acceptable",
    "It was neither good nor bad", "An ordinary experience",
]

# 1 = Positive, 0 = Negative; 2 = Neutral
labels = np.array([
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    2, 2, 2, 2, 2, 2
], dtype=np.int32)

tf.random.set_seed(42)
np.random.seed(42)

tokenizer = Tokenizer(num_words=3000, oov_token="<OOV>")
tokenizer.fit_on_texts(texts)

sequences = tokenizer.texts_to_sequences(texts)
max_length = 20
X = pad_sequences(sequences, maxlen=max_length, padding="post")

model = Sequential([
    Embedding(input_dim=3000, output_dim=32, input_length=max_length),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation="relu"),
    Dense(3, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print("Training the RNN/LSTM model...")
model.fit(X, labels, epochs=100, batch_size=4, verbose=0)
print("Training completed.")

model.save(MODEL_DIR / "sentiment_model.keras")

with open(MODEL_DIR / "tokenizer.json", "w", encoding="utf-8") as f:
    f.write(tokenizer.to_json())

with open(MODEL_DIR / "config.json", "w", encoding="utf-8") as f:
    json.dump({
        "max_length": max_length,
        "classes": ["Negative", "Positive", "Neutral"]
    }, f, indent=2)

print("Model saved in:", MODEL_DIR)
print("Files created: sentiment_model.keras, tokenizer.json, config.json")