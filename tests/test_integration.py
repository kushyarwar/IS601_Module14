"""
Integration tests for Module 14.
Covers JWT auth plus user-scoped BREAD operations for calculations.
"""


def _register(client, username="testuser", email=None, password="pass1234"):
    if email is None:
        email = f"{username}@example.com"
    res = client.post("/users/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    assert res.status_code == 201, res.text
    data = res.json()
    return data["user"]["id"], data["token"]


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _add_calc(client, token, a=10, b=5, op="Add"):
    res = client.post(
        "/calculations",
        json={"a": a, "b": b, "type": op},
        headers=_headers(token),
    )
    assert res.status_code == 201, res.text
    return res.json()


def test_register_and_login_return_jwt(client):
    res = client.post("/users/register", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["user"]["username"] == "alice"
    assert data["user"]["email"] == "alice@example.com"
    assert len(data["token"].split(".")) == 3

    login = client.post("/users/login", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    assert login.status_code == 200
    assert len(login.json()["token"].split(".")) == 3


def test_register_rejects_duplicate_email(client):
    _register(client, "dup1", "dup@example.com")
    res = client.post("/users/register", json={
        "username": "dup2",
        "email": "dup@example.com",
        "password": "pass1234",
    })
    assert res.status_code == 400


def test_login_rejects_wrong_password(client):
    _register(client, "wrongpass", password="correct123")
    res = client.post("/users/login", json={
        "email": "wrongpass@example.com",
        "password": "badpass123",
    })
    assert res.status_code == 401


def test_add_calculation_uses_logged_in_user(client):
    user_id, token = _register(client, "calc_owner")
    data = _add_calc(client, token, 10, 5, "Add")
    assert data["a"] == 10.0
    assert data["b"] == 5.0
    assert data["type"] == "Add"
    assert data["result"] == 15.0
    assert data["user_id"] == user_id


def test_all_operations_compute_correct_result(client):
    _, token = _register(client, "ops")
    assert _add_calc(client, token, 9, 4, "Sub")["result"] == 5.0
    assert _add_calc(client, token, 6, 7, "Multiply")["result"] == 42.0
    assert _add_calc(client, token, 15, 3, "Divide")["result"] == 5.0


def test_browse_returns_only_logged_in_users_calculations(client):
    _, token_a = _register(client, "owner_a")
    _, token_b = _register(client, "owner_b")
    own = _add_calc(client, token_a, 1, 2, "Add")
    _add_calc(client, token_b, 9, 9, "Multiply")

    res = client.get("/calculations", headers=_headers(token_a))

    assert res.status_code == 200
    rows = res.json()
    assert len(rows) == 1
    assert rows[0]["id"] == own["id"]
    assert rows[0]["result"] == 3.0


def test_read_calculation_by_id(client):
    _, token = _register(client, "reader")
    created = _add_calc(client, token, 4, 4, "Add")

    res = client.get(f"/calculations/{created['id']}", headers=_headers(token))

    assert res.status_code == 200
    assert res.json()["result"] == 8.0


def test_read_other_users_calculation_returns_404(client):
    _, owner_token = _register(client, "real_owner")
    _, other_token = _register(client, "other_user")
    created = _add_calc(client, owner_token, 4, 4, "Add")

    res = client.get(f"/calculations/{created['id']}", headers=_headers(other_token))

    assert res.status_code == 404


def test_edit_calculation_recomputes_result(client):
    _, token = _register(client, "editor")
    created = _add_calc(client, token, 10, 2, "Add")

    res = client.put(
        f"/calculations/{created['id']}",
        json={"a": 20, "b": 4, "type": "Divide"},
        headers=_headers(token),
    )

    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "Divide"
    assert data["result"] == 5.0


def test_patch_calculation_partial_update(client):
    _, token = _register(client, "patcher")
    created = _add_calc(client, token, 6, 3, "Add")

    res = client.patch(
        f"/calculations/{created['id']}",
        json={"type": "Multiply"},
        headers=_headers(token),
    )

    assert res.status_code == 200
    assert res.json()["result"] == 18.0


def test_delete_calculation(client):
    _, token = _register(client, "deleter")
    created = _add_calc(client, token, 2, 2, "Multiply")

    delete_res = client.delete(f"/calculations/{created['id']}", headers=_headers(token))
    read_res = client.get(f"/calculations/{created['id']}", headers=_headers(token))

    assert delete_res.status_code == 204
    assert read_res.status_code == 404


def test_delete_other_users_calculation_returns_404(client):
    _, owner_token = _register(client, "delete_owner")
    _, other_token = _register(client, "delete_other")
    created = _add_calc(client, owner_token, 8, 2, "Divide")

    res = client.delete(f"/calculations/{created['id']}", headers=_headers(other_token))

    assert res.status_code == 404


def test_calculation_routes_require_auth(client):
    assert client.get("/calculations").status_code == 401
    assert client.post("/calculations", json={"a": 1, "b": 2, "type": "Add"}).status_code == 401
    assert client.get("/calculations/1").status_code == 401
    assert client.put("/calculations/1", json={"a": 3}).status_code == 401
    assert client.delete("/calculations/1").status_code == 401


def test_invalid_token_rejected(client):
    res = client.get("/calculations", headers={"Authorization": "Bearer bad-token"})
    assert res.status_code == 401


def test_invalid_calculation_inputs(client):
    _, token = _register(client, "badcalc")
    invalid_type = client.post(
        "/calculations",
        json={"a": 5, "b": 3, "type": "Power"},
        headers=_headers(token),
    )
    divide_zero = client.post(
        "/calculations",
        json={"a": 5, "b": 0, "type": "Divide"},
        headers=_headers(token),
    )
    missing_number = client.post(
        "/calculations",
        json={"a": "abc", "b": 2, "type": "Add"},
        headers=_headers(token),
    )

    assert invalid_type.status_code == 422
    assert divide_zero.status_code == 422
    assert missing_number.status_code == 422


def test_delete_user_cascades_own_calculations(client):
    user_id, token = _register(client, "cascade_user")
    created = _add_calc(client, token, 5, 5, "Add")

    assert client.delete(f"/users/{user_id}").status_code == 204
    assert client.get(f"/calculations/{created['id']}", headers=_headers(token)).status_code == 401


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
