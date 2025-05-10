

# from modules.extract_features import extract_features

# from modules.extract_features import extract_features
#from modules.extract_features import extract_features
from flask import Flask, jsonify, request, abort
import sys
import os
import pickle
import pandas as pd

sys.path.append(os.path.abspath(os.path.join('..')))
from modules.feature_engineering import feature_engineering
app = Flask(__name__)


@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.get_json()
    url = data.get('url')
    if url is None:
        abort(400)
    model = load_model()

    features = feature_engineering(url)
    input_data = pd.DataFrame([features])
    print(input_data)
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


def extract_features_from_url(url):
    features = extract_features(url)
    return features


def load_model():
    model = pickle.load(
        open('../reports/random_forest_classifier.pkl', 'rb'))
    return model


if __name__ == "__main__":
    app.run(debug=True)
