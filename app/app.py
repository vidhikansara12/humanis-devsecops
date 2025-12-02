from functools import wraps

from flask import Flask, jsonify, request, abort
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# In-memory store for demo purposes
ITEMS = {}
NEXT_ID = 1

# Prometheus metrics (lazily initialized)
REQUEST_COUNT = None


def create_app():
    global REQUEST_COUNT

    # Initialize the Counter only once per process
    if REQUEST_COUNT is None:
        REQUEST_COUNT = Counter(
            "flask_app_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "http_status"],
        )

    app = Flask(__name__)

    def track_request(endpoint_name):
        """Decorator to track requests for each endpoint."""
        def decorator(func):
            @wraps(func)  # preserve original function name & metadata
            def wrapper(*args, **kwargs):
                response = func(*args, **kwargs)
                status_code = response[1] if isinstance(response, tuple) else 200
                REQUEST_COUNT.labels(
                    request.method, endpoint_name, status_code
                ).inc()
                return response
            return wrapper
        return decorator

    @app.route("/health", methods=["GET"])
    @track_request("health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/items", methods=["GET"])
    @track_request("list_items")
    def list_items():
        """Return list of all items."""
        return jsonify(list(ITEMS.values())), 200

    @app.route("/items", methods=["POST"])
    @track_request("create_item")
    def create_item():
        """Create a new item: expects JSON with 'name'."""
        global NEXT_ID

        data = request.get_json()
        if not data or "name" not in data:
            abort(400, "Missing 'name' field")

        item = {
            "id": NEXT_ID,
            "name": data["name"],
        }
        ITEMS[NEXT_ID] = item
        NEXT_ID += 1
        return jsonify(item), 201

    @app.route("/items/<int:item_id>", methods=["GET"])
    @track_request("get_item")
    def get_item(item_id):
        """Get a single item by ID."""
        item = ITEMS.get(item_id)
        if not item:
            abort(404, "Item not found")
        return jsonify(item), 200

    @app.route("/items/<int:item_id>", methods=["PUT"])
    @track_request("update_item")
    def update_item(item_id):
        """Update an existing item: expects JSON with 'name'."""
        item = ITEMS.get(item_id)
        if not item:
            abort(404, "Item not found")

        data = request.get_json()
        if not data or "name" not in data:
            abort(400, "Missing 'name' field")

        item["name"] = data["name"]
        return jsonify(item), 200

    @app.route("/items/<int:item_id>", methods=["DELETE"])
    @track_request("delete_item")
    def delete_item(item_id):
        """Delete an item by ID."""
        item = ITEMS.pop(item_id, None)
        if not item:
            abort(404, "Item not found")
        return "", 204

    @app.route("/metrics")
    def metrics():
        """Prometheus metrics endpoint."""
        return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
