import pytest
from app.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset in-memory store between tests (optional safety)
        from app.app import ITEMS, NEXT_ID
        ITEMS.clear()
        NEXT_ID = 1
        yield client


def test_list_items_initially_empty(client):
    resp = client.get("/items")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data == []


def test_create_and_get_item(client):
    # Create item
    resp = client.post("/items", json={"name": "Item 1"})
    assert resp.status_code == 201
    item = resp.get_json()
    assert "id" in item
    assert item["name"] == "Item 1"

    # Get item by id
    item_id = item["id"]
    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    fetched = resp.get_json()
    assert fetched["id"] == item_id
    assert fetched["name"] == "Item 1"


def test_update_item(client):
    # Create
    resp = client.post("/items", json={"name": "Old"})
    item_id = resp.get_json()["id"]

    # Update
    resp = client.put(f"/items/{item_id}", json={"name": "New"})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated["name"] == "New"


def test_delete_item(client):
    # Create
    resp = client.post("/items", json={"name": "ToDelete"})
    item_id = resp.get_json()["id"]

    # Delete
    resp = client.delete(f"/items/{item_id}")
    assert resp.status_code == 204

    # Confirm it 404s afterwards
    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 404
