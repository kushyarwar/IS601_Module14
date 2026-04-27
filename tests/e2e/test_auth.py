"""
Playwright E2E tests for Module 14 front-end flows.
"""
import httpx
import pytest

SERVER_URL = "http://127.0.0.1:8001"


# ── Positive Tests ─────────────────────────────────────────────────────────────

def test_register_valid_data(page, live_server):
    page.goto(f"{SERVER_URL}/static/register.html")
    page.fill("#email", "newuser@example.com")
    page.fill("#password", "securepass123")
    page.fill("#confirm_password", "securepass123")
    page.click("button[type=submit]")
    page.wait_for_selector("#success-msg", state="visible", timeout=8000)
    text = page.inner_text("#success-msg").lower()
    assert "success" in text


def test_login_valid_credentials(page, live_server):
    httpx.post(f"{SERVER_URL}/register", json={
        "email": "loginuser@example.com",
        "password": "securepass123",
    })

    page.goto(f"{SERVER_URL}/static/login.html")
    page.fill("#email", "loginuser@example.com")
    page.fill("#password", "securepass123")
    page.click("button[type=submit]")
    page.wait_for_selector("#success-msg", state="visible", timeout=8000)
    text = page.inner_text("#success-msg").lower()
    assert "success" in text


def test_calculation_bread_flow(page, live_server):
    res = httpx.post(f"{SERVER_URL}/register", json={
        "email": "breaduser@example.com",
        "password": "securepass123",
    })
    token = res.json()["token"]

    page.goto(f"{SERVER_URL}/static/calculations.html")
    page.evaluate("(token) => localStorage.setItem('jwt_token', token)", token)
    page.reload()

    page.fill("#a", "8")
    page.fill("#b", "4")
    page.select_option("#type", "Add")
    page.click("#save-btn")
    page.wait_for_selector("#success-msg", state="visible", timeout=8000)
    assert "created" in page.inner_text("#success-msg").lower()
    assert "12" in page.inner_text("#calc-list")

    page.click("button[data-action='read']")
    page.wait_for_selector("#detail-box", state="visible", timeout=5000)
    assert "12" in page.inner_text("#detail-box")

    page.click("button[data-action='edit']")
    page.wait_for_function("document.querySelector('#calc-id').value !== ''")
    page.fill("#a", "20")
    page.fill("#b", "5")
    page.select_option("#type", "Divide")
    page.click("#save-btn")
    page.wait_for_selector("#success-msg", state="visible", timeout=8000)
    assert "updated" in page.inner_text("#success-msg").lower()
    assert "Divide" in page.inner_text("#calc-list")
    assert "4" in page.inner_text("#calc-list")

    page.click("button[data-action='delete']")
    page.wait_for_selector("#success-msg", state="visible", timeout=8000)
    assert "deleted" in page.inner_text("#success-msg").lower()
    page.wait_for_selector("#empty-msg", state="visible", timeout=5000)


# ── Negative Tests ─────────────────────────────────────────────────────────────

def test_register_short_password_shows_frontend_error(page, live_server):
    page.goto(f"{SERVER_URL}/static/register.html")
    page.fill("#email", "shortpass@example.com")
    page.fill("#password", "abc")
    page.fill("#confirm_password", "abc")
    page.click("button[type=submit]")
    page.wait_for_selector("#error-msg", state="visible", timeout=5000)
    text = page.inner_text("#error-msg").lower()
    assert "password" in text


def test_calculation_divide_by_zero_shows_frontend_error(page, live_server):
    res = httpx.post(f"{SERVER_URL}/register", json={
        "email": "dividezero@example.com",
        "password": "securepass123",
    })
    token = res.json()["token"]

    page.goto(f"{SERVER_URL}/static/calculations.html")
    page.evaluate("(token) => localStorage.setItem('jwt_token', token)", token)
    page.reload()
    page.fill("#a", "9")
    page.fill("#b", "0")
    page.select_option("#type", "Divide")
    page.click("#save-btn")
    page.wait_for_selector("#error-msg", state="visible", timeout=5000)
    assert "division by zero" in page.inner_text("#error-msg").lower()


def test_calculations_without_login_shows_error(page, live_server):
    page.goto(f"{SERVER_URL}/static/calculations.html")
    page.evaluate("localStorage.removeItem('jwt_token')")
    page.reload()
    page.wait_for_selector("#error-msg", state="visible", timeout=5000)
    assert "login" in page.inner_text("#error-msg").lower()


def test_login_wrong_password_shows_error(page, live_server):
    httpx.post(f"{SERVER_URL}/register", json={
        "email": "wrongpass@example.com",
        "password": "correctpass123",
    })

    page.goto(f"{SERVER_URL}/static/login.html")
    page.fill("#email", "wrongpass@example.com")
    page.fill("#password", "totallyWrongPass999")
    page.click("button[type=submit]")
    page.wait_for_selector("#error-msg", state="visible", timeout=8000)
    text = page.inner_text("#error-msg").lower()
    assert "invalid" in text
