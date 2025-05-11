from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_page_content(url: str, max_tokens=1000):
    '''
    Scrapes webpage content from a remote url
     - returns a dictionary of type, content, metadata
    '''
    try:
        browser = init_browser(url)
        wait = WebDriverWait(browser, 10)
        body = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))).text
        body = " ".join(body.splitlines())
        description = ""
        try:
            description = wait.until(
                EC.presence_of_element_located((By.XPATH, "//meta[@name='description']"))).get_attribute("content")
        except:
            pass

        try:
            keywords = wait.until(
                EC.presence_of_element_located((By.XPATH, "//meta[@name='keywords']"))).get_attribute("content")
        except:
            keywords = None

        content = {
            "type": "webpage",
            "content": body[:max_tokens],
            "metadata": {
                "title": browser.title,
                "url": url,
                "description": description[:int(max_tokens/2)] if description else '',
                "keywords": keywords if keywords else '',

            }
        }
        browser.close()
        return content
    except Exception as e:
        print(e)
        return None


def init_browser(url: str) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        argument="User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0")
    options.page_load_strategy = 'eager'
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    return browser


if __name__ == "__main__":
    print(get_page_content("https://www.mdpi.com/1099-4300/23/2/182"))
    print(get_page_content("https://nextjs.org/"))
