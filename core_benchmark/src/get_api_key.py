import os
from typing import Any, cast

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Selectors
selectors = {
    "usernameInput": '//input[@id="username"]',
    "passwordInput": '//input[@id="password"]',
    "continueButton": '//button[text()="Continue"]',
    "apiDocLink": '//a[@id="API Documentation_nav_link"]',
    "generateButton": '//div[@id="apiDocumentation_generateKey_button"]',
    "apiKeyInput": '//input[@type="text"]',
}

# Credentials
credentials = {"username": os.getenv("USER_NAME"), "password": os.getenv("PASSWORD")}


def enter_username(page: Any, username: str) -> None:
    page.wait_for_selector(selectors["usernameInput"])
    page.fill(selectors["usernameInput"], username)


def enter_password(page: Any, password: str) -> None:
    page.wait_for_selector(selectors["passwordInput"])
    page.fill(selectors["passwordInput"], password)


def click_on_continue_button(page: Any) -> None:
    page.wait_for_selector(selectors["continueButton"])
    page.locator(selectors["continueButton"]).click()


def login(page: Any) -> None:
    enter_username(page, credentials["username"])
    enter_password(page, credentials["password"])
    click_on_continue_button(page)


def force_redirection(page: Any, url: str) -> None:
    page.goto(url)
    page.wait_for_url(url)


def click_on_api_doc(page: Any) -> None:
    link_locator = page.locator(selectors["apiDocLink"])
    link_locator.click()


def generate_api_key(page: Any) -> None:
    btn_locator = page.locator(selectors["generateButton"])
    btn_locator.click()


def get_api_key(page: Any) -> str:
    click_on_api_doc(page)
    page.wait_for_timeout(1000)
    input_locator = page.locator(selectors["apiKeyInput"])
    input_locator.wait_for(state="attached")

    api_key = page.eval_on_selector(selectors["apiKeyInput"], "input => input.value")

    if api_key == "No API Key to be displayed ,please generate one !":
        generate_api_key(page)
        page.wait_for_timeout(2000)
        api_key = page.eval_on_selector(selectors["apiKeyInput"], "input => input.value")

    return cast(str, api_key)


def before_all() -> None:
    with sync_playwright() as p:
        retry_count = 1
        while retry_count <= 3:
            try:
                browser = p.chromium.launch()
                context = browser.new_context(viewport=None)
                page = context.new_page()
                web_url = os.getenv("WEB_URL")
                page.goto(web_url)
                page.locator(selectors["continueButton"]).wait_for()
                login(page)
                api_key = get_api_key(page)
                print(f"API Key: {api_key}")
                break
            except Exception as error:
                print(f"Pre-Setup failed. Retrying... ({retry_count} attempts left)", error)
                page.screenshot(
                    path=f"./Screenshots/beforeAll_retry_{retry_count}.png", full_page=True
                )
                retry_count += 1
            finally:
                browser.close()


before_all()
