
from flask import Flask, jsonify, request, abort
import sys
import os
import pickle
import pandas as pd
import logging
from urllib.parse import urlparse
from os.path import splitext
from transcribe_audio import transcribe_audio
from extract_pdf import read_remote_pdf
from gemini import classify_content
from json import JSONEncoder
from scrapper import get_page_content

sys.path.append(os.path.abspath(os.path.join('..')))

from modules.feature_engineering import feature_engineering
from modules.fetch_domain_info import get_domain_info
from modules.extract_url_components import get_ext, normalise_url

app = Flask(__name__)

@app.route('/api/classify', methods=['POST'])
def classify():
    data = request.get_json()
    url = data.get('url')
    if url is None:
        abort(400)
    url_ext = get_ext(url)
    texts = None
    if url_ext:
   
        exe_file = executable_files_result(url_ext)
        if exe_file:
            return jsonify(exe_file), 200
        elif is_audio(url_ext):
            texts = transcribe_audio(url)
        elif url_ext == 'pdf':
            texts = read_remote_pdf(url)

    if not texts:
        texts = get_page_content(url)
    res = None   
    if texts:
        content = JSONEncoder().encode(texts)
        res = classify_content(content)
    if not res:
        res = classify_url(url)
    return jsonify(res), 200


def executable_files_result(ext):
    executables = {'exe', 'bat', 'cmd', 'sh', 'msi', 'scr', 'vbs', 'pif', 'com', 'ps1',
                   'app', 'jar', 'py', 'dll', 'lnk', 'bin'}
    if ext not in executables:
        return None
    return {
        'classification': 'unsafe',
        'confidence': 1,
        'details': 'Executable file detected',
        'reasons': ['executable']
    }



def is_audio(ext):
    return ext in ['mp3', 'wav', 'aac', 'ogg', 'flac']


def classify_url(url):
    model = load_model()

    features = feature_engineering(url)
    domain_info = get_domain_info(url)
    print(f"Domain info: {domain_info}")
    input_data = pd.DataFrame([domain_info, features])

    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)
    return prediction_result(int(prediction[0]), probability)


def prediction_result(prediction, probability):
    confidence = float(probability[0][prediction])
    classification = "safe" if prediction == 0 else "unsafe"
    reason = 'phishing'
    if prediction == 0:
        reason = 'benign'
    elif prediction == 2:
        reason = 'defacement'
    elif prediction == 3:
        reason = 'malware'
    return {
        "classification": classification,
        "confidence": confidence,
        "reasons": [reason],
        "details": ""
    }


def load_model():
    model = pickle.load(
        open('../reports/random_forest_classifier_mn.pkl', 'rb'))
    return model


if __name__ == "__main__":
    app.run(debug=True)
