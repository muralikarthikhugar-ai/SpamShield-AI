
# ==========================================
# SPAMSHIELD AI
# SMS SPAM DETECTION - MODEL TRAINING
# ==========================================

# 1. Import libraries

import pandas as pd
import numpy as np
import re
import os
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# 2. LOAD DATASET
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(
    "data/spam.csv",
    encoding="latin-1"
)

print("Original dataset shape:", df.shape)


# ==========================================
# 3. DATA CLEANING
# ==========================================

print("\nCleaning dataset...")

# First column contains labels
labels = df.iloc[:, 0]

# All remaining columns may contain message text
message_columns = df.iloc[:, 1:]

# Combine message fragments into one message
messages = message_columns.fillna("").astype(str).apply(
    lambda row: " ".join(
        value.strip()
        for value in row
        if value.strip() and value.strip().lower() != "nan"
    ),
    axis=1
)

# Create a clean DataFrame
df = pd.DataFrame({
    "label": labels,
    "message": messages
})

# Remove rows with missing labels or messages
df.dropna(inplace=True)

df["label"] = df["label"].astype(str).str.strip().str.lower()

df["message"] = df["message"].astype(str).str.strip()

df = df[
    df["label"].isin(["ham", "spam"])
]

df = df[
    df["message"].str.len() > 0
]

# Remove duplicate messages
df.drop_duplicates(
    subset=["label", "message"],
    inplace=True
)

# Save cleaned dataset
os.makedirs("data", exist_ok=True)

df.to_csv(
    "data/cleaned_spam.csv",
    index=False
)

print("Cleaned dataset saved successfully!")

df.reset_index(drop=True, inplace=True)

print("Cleaned dataset shape:", df.shape)

print("\nClass distribution:")
print(df["label"].value_counts())


# ==========================================
# 4. TEXT PREPROCESSING
# ==========================================

print("\nPreprocessing messages...")

def clean_text(text):

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Replace URLs with a common token
    text = re.sub(
        r"http\S+|www\S+",
        " URL ",
        text
    )

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


df["message"] = df["message"].apply(clean_text)


# ==========================================
# 5. ENCODE LABELS
# ==========================================

# Ham = 0
# Spam = 1

df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})

X = df["message"]
y = df["label"]


# ==========================================
# 6. TRAIN-TEST SPLIT
# ==========================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 7. DEFINE MACHINE LEARNING MODELS
# ==========================================

models = {

    "Multinomial Naive Bayes":
        MultinomialNB(),

    "Logistic Regression":
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ),

    "Linear SVM":
        CalibratedClassifierCV(
            estimator=LinearSVC(
                class_weight="balanced",
                random_state=42
            ),
            cv=3
        )
}


# ==========================================
# 8. TRAIN AND EVALUATE MODELS
# ==========================================

print("\nStarting model training...")

results = {}

best_model = None
best_model_name = None
best_f1 = -1

best_predictions = None

for name, classifier in models.items():

    print("\nTraining:", name)

    # Create ML pipeline
    pipeline = Pipeline([

        # Convert text into numerical features
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                strip_accents="unicode",
                sublinear_tf=True
            )
        ),

        # Machine learning classifier
        (
            "classifier",
            classifier
        )
    ])

    # Train model
    pipeline.fit(X_train, y_train)

    # Predict test data
    predictions = pipeline.predict(X_test)

    # Calculate evaluation metrics
    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    # Save model performance
    results[name] = {

        "accuracy": float(accuracy),

        "precision": float(precision),

        "recall": float(recall),

        "f1_score": float(f1),

        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=["Ham", "Spam"],
            output_dict=True,
            zero_division=0
        )
    }

    # Display results
    print("\nModel:", name)

    print("Accuracy:", round(accuracy * 100, 2), "%")

    print("Precision:", round(precision * 100, 2), "%")

    print("Recall:", round(recall * 100, 2), "%")

    print("F1 Score:", round(f1 * 100, 2), "%")

    # Select model based on spam F1 score
    if f1 > best_f1:

        best_f1 = f1

        best_model = pipeline

        best_model_name = name

        best_predictions = predictions


# ==========================================
# 9. CONFUSION MATRIX
# ==========================================

print("\nBest Model Confusion Matrix:")

cm = confusion_matrix(
    y_test,
    best_predictions,
    labels=[0, 1]
)

print(cm)


# ==========================================
# 10. SAVE BEST MODEL
# ==========================================

os.makedirs("models", exist_ok=True)

joblib.dump(
    best_model,
    "models/spam_model.pkl"
)

print("\nBest model saved successfully!")


# ==========================================
# 11. SAVE MODEL METRICS
# ==========================================

metrics = {

    "best_model": best_model_name,

    "best_f1_score": float(best_f1),

    "training_samples": len(X_train),

    "testing_samples": len(X_test),

    "results": results,

    "confusion_matrix": cm.tolist()
}

with open(
    "models/metrics.json",
    "w"
) as file:

    json.dump(
        metrics,
        file,
        indent=4
    )


# ==========================================
# 12. FINAL RESULTS
# ==========================================

print("\n================================")

print("SPAMSHIELD AI - TRAINING COMPLETED")

print("================================")

print("Best Algorithm:", best_model_name)

print(
    "Best F1 Score:",
    round(best_f1 * 100, 2),
    "%"
)

print("Model saved: models/spam_model.pkl")

print("Metrics saved: models/metrics.json")

print("================================")
