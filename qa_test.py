from playwright.sync_api import sync_playwright, expect

URL = "http://127.0.0.1:8000/login"
USERNAME = "admin"
PASSWORD = "admin"

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
        headless=False
    )
    page = browser.new_page()

    print("Abriendo login...")
    page.goto(URL)

    try:
        # Locators más robustos (ajusta según tu HTML real)
        page.get_by_label("Username").fill(USERNAME)          # o get_by_placeholder("Usuario")
        page.get_by_label("Password").fill(PASSWORD)
        
        print("Intentando login...")
        page.get_by_role("button", name="Iniciar sesión").click()  # o get_by_text("Login")

        # Espera inteligente
        page.wait_for_url("**/dashboard**", timeout=10000)

        print("Página actual:", page.url)
        expect(page).to_have_url(..., timeout=5000)  # puedes agregar regex

        # Verifica contenido real
        expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

        print("✅ Login exitoso")

    except Exception as e:
        print("❌ Error durante el test:", str(e))
        # Opcional: screenshot para debug
        page.screenshot(path="login_error.png")

    finally:
        browser.close()