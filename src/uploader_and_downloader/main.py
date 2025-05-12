import os
import platform
import time
import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def activate_driver(headless=False):
    options = Options()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    if platform.system() == 'Darwin':
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service = service, options = options)
        return driver
    elif platform.system() == 'Linux':
        driver = webdriver.Chrome(options = options)
        return driver
    else:
        print('Unsupport OS')
    return None

def login(driver):
    driver.get('https://jaxa.krpc.jp/user-auth')

    wait = WebDriverWait(driver, 10)
    username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Account ID']")))
    password_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")
    login_button = driver.find_element(By.CSS_SELECTOR, "button.login-form-button")

    load_dotenv()
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    driver.set_window_size(1200, 800)
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    wait = WebDriverWait(driver, 30)
    wait.until(lambda d: 'user-auth' not in d.current_url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    driver.save_screenshot('sc1.png')

def get_into_simulation_page(driver):
    simulation_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.navbar-link[href='/simulation']")))
    simulation_button.click()

    wait = WebDriverWait(driver, 30)
    wait.until(lambda d: 'simulation' in d.current_url)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    # time.sleep(10)

    driver.save_screenshot('sc2.png')

def upload_one_apk(driver, apk_file_path):
    apk_file_path = os.path.abspath(apk_file_path)

    try:
        drop = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "my-dropzone0"))
        )

        input_element = driver.find_element(By.CSS_SELECTOR, "input[type='file']")

        input_element.send_keys(apk_file_path)

        print(f'Successfully upload file: {apk_file_path}')

        # time.sleep(10)
        driver.save_screenshot('sc3.png')

    except Exception as e:
        print(f'Failed to upload apk: {e}')

def click_start_simulation(driver):
    try:
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button--start"))
        )

        start_button.click()
        print('Successfully click start simulation')

        # time.sleep(10)
        driver.save_screenshot('sc4.png')
        
        return True
    except Exception as e:
        print(f'Failed to click Start Simulatin: {e}')

def click_ok_button(driver):
    try:
        js_script = """
        var okButton = document.querySelector('button.ok-button');
        if (okButton) {
            okButton.click();
            return true;
        }
        return false;
        """

        result = driver.execute_script(js_script)
        time.sleep(60)
        driver.save_screenshot('sc5.png')
        if result:
            print('JS Successfully click ok')
            return True
        else:
            print('JS unable to find ok button')
            return False
    except Exception as e:
        print(f'Failed to click span in OK: {e}')

def get_slot_status(driver):
    try:
        slot_status_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.slot-status"))
        )

        status_text = slot_status_element.text.strip()
        return status_text
    except Exception as e:
        print(f'Failed to check slot status: {e}')
        return None

def get_into_result_page(driver):
    try:
        view_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button--view"))
        )

        view_button.click()

        print('Successfully click view result')

        time.sleep(20)
        return True

    except Exception as e:
        print('Failed to click view result: {e}')
        return False

def download_result_img(driver):
    time.sleep(30)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    try:
        js_script = """
            var downloadButtons = document.querySelectorAll('button.footer-button.button-download');

            for (let i = 0; i < downloadButtons.length; ++i) {
                if (downloadButtons[i].textContent.includes('Download Image Files')) {
                    downloadButtons[i].click();
                    return true;
                }
            }
            return false;
        """

        result = driver.execute_script(js_script)

        if result:
            print('js Successfully click download image files')
        else:
            print('js unable to click or locate download image files')

    except Exception as e:
        print(f'Failed to click download image files: {e}')

def go_back_to_simulation_page(driver):
    driver.get('https://jaxa.krpc.jp/simulation')

def main():
    driver = activate_driver()
    login(driver)
    get_into_simulation_page(driver)
    while True:
        print(datetime.datetime.now(), end=' - ')
        slot_status = get_slot_status(driver)
        print(f'slot status: {slot_status}')
        if slot_status == 'Available':
            upload_one_apk(driver, '/home/yuc/Downloads/6thKiboSampleAPK/SampleApk/app/build/outputs/apk/debug/app-debug.apk')
            click_start_simulation(driver)
            click_ok_button(driver)
        elif slot_status == 'Finished':
            get_into_result_page(driver)
            download_result_img(driver)
            go_back_to_simulation_page(driver)
        time.sleep(300)
        driver.refresh()
    driver.quit()

if __name__ == '__main__':
    main()
