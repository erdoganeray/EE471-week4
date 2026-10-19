"""Flask server: serves the calculator page and the calculation API."""
from flask import Flask, jsonify, request

from web_calculator import WebCalculator

# Files in static/ are served from the root URL: /style.css, /script.js
app = Flask(__name__, static_folder="static", static_url_path="")
calculator = WebCalculator()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/calculate")
def calculate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    try:
        result = calculator.calculate(data.get("a"), data.get("operator"), data.get("b"))
    except (ValueError, ZeroDivisionError) as error:
        return jsonify(error=str(error)), 400

    return jsonify(result=result)


if __name__ == "__main__":
    app.run(debug=True)
