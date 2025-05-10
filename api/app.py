

from flask import Flask, jsonify, request, abort
import sys
import os
import pickle
import pandas as pd
import logging

sys.path.append(os.path.abspath(os.path.join('..')))

from modules.feature_engineering import feature_engineering
from modules.fetch_domain_info import get_domain_info

app = Flask(__name__)


@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.get_json()
    url = data.get('url')
    if url is None:
        abort(400)
    model = load_model()

    features = feature_engineering(url)
    domain_info = get_domain_info(url)
    print(f"Domain info: {domain_info}")
    input_data = pd.DataFrame([domain_info, features])

    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)
    return jsonify({'prediction': {
        'phishing': prediction_result(int(prediction[0])), 'probability': float(probability[0][int(prediction[0])])}}), 200


def prediction_result(prediction) -> str:
    print(prediction)
    if prediction == 0:
        return 'benign'
    elif prediction == 2:
        return 'defacement'
    elif prediction == 3:
        return 'malware'
    else:
        return 'phishing'


def load_model():
    model = pickle.load(
        open('../reports/random_forest_classifier.pkl', 'rb'))
    return model


if __name__ == "__main__":
    app.run(debug=True)
