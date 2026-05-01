import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:8000"

def register_and_login(page: Page, username="e2euser", password="e2epass123"):
    page.goto(f"{BASE}/register")
    page.fill("input[name=username]", username)
    page.fill("input[name=email]", f"{username}@test.com")
    page.fill("input[name=password]", password)
    page.click("button[type=submit]")
    page.goto(f"{BASE}/login")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", password)
    page.click("button[type=submit]")

# ── Positive E2E ─────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_e2e_register_login(page: Page):
    register_and_login(page, "newuser1", "pass1234")
    expect(page).to_have_url(f"{BASE}/calculations")

@pytest.mark.e2e
def test_e2e_add_calculation(page: Page):
    register_and_login(page, "adduser", "pass1234")
    page.click("text=+ New Calculation")
    page.select_option("select[name=operation]", "add")
    page.fill("input[name=operand1]", "15")
    page.fill("input[name=operand2]", "25")
    page.click("button[type=submit]")
    expect(page.locator("table")).to_contain_text("40")

@pytest.mark.e2e
def test_e2e_edit_calculation(page: Page):
    register_and_login(page, "edituser", "pass1234")
    page.click("text=+ New Calculation")
    page.select_option("select[name=operation]", "add")
    page.fill("input[name=operand1]", "1")
    page.fill("input[name=operand2]", "1")
    page.click("button[type=submit]")
    page.click("text=Edit")
    page.select_option("select[name=operation]", "multiply")
    page.fill("input[name=operand1]", "6")
    page.fill("input[name=operand2]", "7")
    page.click("button[type=submit]")
    expect(page.locator("table")).to_contain_text("42")

@pytest.mark.e2e
def test_e2e_delete_calculation(page: Page):
    register_and_login(page, "deluser", "pass1234")
    page.click("text=+ New Calculation")
    page.select_option("select[name=operation]", "subtract")
    page.fill("input[name=operand1]", "10")
    page.fill("input[name=operand2]", "3")
    page.click("button[type=submit]")
    page.on("dialog", lambda d: d.accept())
    page.click("button.danger")
    expect(page.locator("main")).to_contain_text("No calculations")

# ── Negative E2E ─────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_e2e_unauthenticated_redirect(page: Page):
    page.goto(f"{BASE}/calculations")
    # Should see login page or 401
    assert "/login" in page.url or "Login" in page.content() or page.status == 401

@pytest.mark.e2e
def test_e2e_divide_by_zero_shows_error(page: Page):
    register_and_login(page, "divuser", "pass1234")
    page.click("text=+ New Calculation")
    page.select_option("select[name=operation]", "divide")
    page.fill("input[name=operand1]", "10")
    page.fill("input[name=operand2]", "0")
    page.click("button[type=submit]")
    # Should show error or stay on form
    assert "error" in page.content().lower() or "divide" in page.url
