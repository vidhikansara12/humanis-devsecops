from flask import Flask, jsonify, request, abort

# In-memory store for demo purposes
ITEMS = {}
NEXT_ID = 1


def create_app():
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/items", methods=["GET"])
    def list_items():
        """Return list of all items."""
        return jsonify(list(ITEMS.values())), 200

    @app.route("/items", methods=["POST"])
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
    def get_item(item_id):
        """Get a single item by ID."""
        item = ITEMS.get(item_id)
        if not item:
            abort(404, "Item not found")
        return jsonify(item), 200

    @app.route("/items/<int:item_id>", methods=["PUT"])
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
    def delete_item(item_id):
        """Delete an item by ID."""
        item = ITEMS.pop(item_id, None)
        if not item:
            abort(404, "Item not found")
        # 204 = No Content
        return "", 204

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
