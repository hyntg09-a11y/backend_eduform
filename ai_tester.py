import requests
from playwright.sync_api import sync_playwright
import sys

LM_URL = "http://localhost:1234/v1/chat/completions"

def ask_llm(prompt):
    data = {
        "model": "qwen2.5",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        r = requests.post(LM_URL, json=data, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error llamando al LLM:", e)
        return None

def is_server_alive(base_url, timeout=4):
    try:
        r = requests.get(base_url, timeout=timeout)
        return 200 <= r.status_code < 400
    except requests.RequestException:
        return False

URL = "http://127.0.0.1:8000"

if not is_server_alive(URL):
    print(f"❌ El servidor no responde en {URL}")
    print("   → Verifica que 'python manage.py runserver' esté corriendo")
    sys.exit(1)

# Si llega aquí → servidor OK, procedemos
print("Servidor responde → iniciando test...")

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
        headless=False
    )
    page = browser.new_page()
    page.goto(URL)

    html = page.content()

    prompt = (
        "You are a QA tester. "
        "What should be tested on this page? "
        f"Page HTML (first 12000 chars):\n{html[:12000]}"
    )

    decision = ask_llm(prompt)
    if decision:
        print("LLM decision:")
        print(decision)
    else:
        print("No se pudo obtener decisión del LLM")

    # ... resto de clicks o lo que tengas

    browser.close()