from flask import Flask, request, jsonify
import requests, re, os

app = Flask(__name__)

def extract_names(text):
    # Simple heuristic for capitalized words
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    stopwords = {"The", "And", "Of", "In", "On", "At", "To", "For", "By"}
    names = [w for w in words if w not in stopwords]
    return names

def genderize_names(names):
    """Use Genderize.io API to detect gender"""
    results = {}
    unique_names = list(set(names))
    for name in unique_names:
        try:
            r = requests.get(f"https://api.genderize.io/?name={name}")
            if r.status_code == 200:
                data = r.json()
                results[name] = data.get("gender", "unknown")
            else:
                results[name] = "unknown"
        except:
            results[name] = "unknown"
    return results

@app.route('/')
def home():
    return "Gender Balance Analyzer backend is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    names = extract_names(text)
    name_counts = {}
    for n in names:
        name_counts[n] = name_counts.get(n, 0) + 1

    gender_map = genderize_names(list(name_counts.keys()))

    male = female = unknown = 0
    for name, g in gender_map.items():
        if g == 'male':
            male += name_counts[name]
        elif g == 'female':
            female += name_counts[name]
        else:
            unknown += name_counts[name]

    total = male + female
    ratio = round(female / total * 100, 1) if total > 0 else 0

    return jsonify({
        "male": male,
        "female": female,
        "unknown": unknown,
        "female_percent": ratio,
        "name_counts": name_counts,
        "gender_map": gender_map
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
