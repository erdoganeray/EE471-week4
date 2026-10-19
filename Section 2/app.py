"""Flask REST API for the library.

The routes only translate HTTP requests into LibraryCollection method calls.
All rules live in custom_classes.py.
"""
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from custom_classes import DVD, Book, ItemNotFoundError, ItemStateError, LibraryCollection

# Files in static/ are served from the root URL: /style.css, /script.js
app = Flask(__name__, static_folder="static", static_url_path="")
app.json.sort_keys = False  # keep the field order of to_dict()

# One collection for the whole server, seeded with mixed item types
library = LibraryCollection()
library.add_item(Book("Dune", "Frank Herbert", page_count=412))
library.add_item(DVD("Interstellar", "Christopher Nolan", duration=169))
arrival_id = library.add_item(DVD("Arrival", "Denis Villeneuve", duration=116))
library.get_item(arrival_id).checkout()
library.add_item(Book("The Hobbit", "J.R.R. Tolkien", page_count=310))


def json_body():
    """Return the request body as a dict, or raise ValueError (400)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")
    return data


# ---------- Errors: exceptions from custom_classes.py become JSON responses ----------

@app.errorhandler(ValueError)
def bad_request(error):
    return jsonify(error=str(error)), 400


@app.errorhandler(ItemNotFoundError)
def not_found(error):
    return jsonify(error=str(error)), 404


@app.errorhandler(ItemStateError)
def conflict(error):
    return jsonify(error=str(error)), 409


@app.errorhandler(HTTPException)
def http_error(error):
    # Flask's own errors, e.g. an unknown URL or a wrong method
    return jsonify(error=error.description), error.code


# ---------- Routes ----------

@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/items")
def create_item():
    data = json_body()
    item = library.create_item(data.pop("type", None), **data)
    return jsonify(item.to_dict()), 201


@app.get("/api/items")
def list_items():
    # "true"/"false" become booleans; any other value is rejected by list_items()
    available = request.args.get("available")
    available = {"true": True, "false": False}.get(available, available)
    items = library.list_items(available=available, item_type=request.args.get("type"))
    return jsonify([item.to_dict() for item in items])


@app.get("/api/items/<int:item_id>")
def get_item(item_id):
    return jsonify(library.get_item(item_id).to_dict())


@app.put("/api/items/<int:item_id>")
def replace_item(item_id):
    return jsonify(library.replace_item(item_id, **json_body()).to_dict())


@app.patch("/api/items/<int:item_id>")
def update_item(item_id):
    return jsonify(library.update_item(item_id, **json_body()).to_dict())


@app.delete("/api/items/<int:item_id>")
def remove_item(item_id):
    library.remove_item(item_id)
    return "", 204


@app.post("/api/items/<int:item_id>/checkout")
def checkout(item_id):
    item = library.get_item(item_id)
    message = item.checkout()
    return jsonify(message=message, item=item.to_dict())


@app.post("/api/items/<int:item_id>/return")
def return_item(item_id):
    item = library.get_item(item_id)
    message = item.return_item()
    return jsonify(message=message, item=item.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
