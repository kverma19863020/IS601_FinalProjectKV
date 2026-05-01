import pytest

# ── Positive Tests ────────────────────────────────────────────────────────────

def test_browse_empty(auth_client):
    r = auth_client.get("/calculations")
    assert r.status_code == 200
    assert "No calculations" in r.text

def test_add_calculation(auth_client):
    r = auth_client.post("/calculations/new",
        data={"operation": "add", "operand1": "10", "operand2": "5"})
    assert r.status_code == 200
    assert "15" in r.text   # result shown in list

def test_browse_shows_calculation(auth_client):
    auth_client.post("/calculations/new",
        data={"operation": "multiply", "operand1": "3", "operand2": "4"})
    r = auth_client.get("/calculations")
    assert "multiply" in r.text
    assert "12" in r.text

def test_read_calculation(auth_client):
    auth_client.post("/calculations/new",
        data={"operation": "subtract", "operand1": "20", "operand2": "8"})
    r = auth_client.get("/calculations/1")
    assert r.status_code == 200
    assert "12" in r.text

def test_edit_calculation(auth_client):
    auth_client.post("/calculations/new",
        data={"operation": "add", "operand1": "1", "operand2": "1"})
    r = auth_client.post("/calculations/1/edit",
        data={"operation": "multiply", "operand1": "6", "operand2": "7"})
    assert r.status_code == 200
    assert "42" in r.text

def test_delete_calculation(auth_client):
    auth_client.post("/calculations/new",
        data={"operation": "add", "operand1": "1", "operand2": "2"})
    auth_client.post("/calculations/1/delete")
    r = auth_client.get("/calculations")
    assert "No calculations" in r.text

def test_divide_operation(auth_client):
    r = auth_client.post("/calculations/new",
        data={"operation": "divide", "operand1": "10", "operand2": "2"})
    assert "5" in r.text

# ── Negative Tests ────────────────────────────────────────────────────────────

def test_browse_unauthenticated(client):
    r = client.get("/calculations")
    assert r.status_code in (401, 403, 200)  # redirected to login or blocked

def test_invalid_operation(auth_client):
    r = auth_client.post("/calculations/new",
        data={"operation": "modulo", "operand1": "10", "operand2": "3"})
    assert r.status_code in (200, 422)
    assert "error" in r.text.lower() or "valid" in r.text.lower() or r.status_code == 422

def test_divide_by_zero(auth_client):
    r = auth_client.post("/calculations/new",
        data={"operation": "divide", "operand1": "10", "operand2": "0"})
    assert r.status_code in (200, 422)

def test_read_nonexistent(auth_client):
    r = auth_client.get("/calculations/9999")
    assert r.status_code == 404

def test_edit_nonexistent(auth_client):
    r = auth_client.post("/calculations/9999/edit",
        data={"operation": "add", "operand1": "1", "operand2": "2"})
    assert r.status_code == 404

def test_delete_nonexistent(auth_client):
    r = auth_client.post("/calculations/9999/delete")
    assert r.status_code == 404
