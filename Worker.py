from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
BASE_URL = "http://127.0.0.1:8000"

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 20)

try:
    driver.get(f"{BASE_URL}/login/")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    time.sleep(2)

    wait.until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys("anikaa@gmail.com")
    wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys("anikaa45")
    time.sleep(2)
    
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
    ).click()
    time.sleep(2)

    view_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/worker/task/104/' and contains(text(), 'View')]")
    ))

    # Scroll to it and click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_button)
    time.sleep(2)
    view_button.click()
    time.sleep(2)

    start_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[contains(@class, 'btn-success') and contains(., 'Start Task')]")
    ))
    start_btn.click()

    in_progress_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[contains(., 'In Progress')]")
    ))
    in_progress_btn.click()
    time.sleep(2)
    complete_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[contains(., 'Completed')]")
    ))
    complete_btn.click()
    time.sleep(2)
    in_progress_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[contains(., 'In Progress')]")
    ))
    in_progress_btn.click()
    time.sleep(2)
    update_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[contains(@href, '/worker/task/update/') and contains(text(), 'Update Status')]")
    ))
    update_btn.click()
    time.sleep(2)


    address_box = wait.until(EC.presence_of_element_located((By.NAME, "additional_notes")))

    # ===== Clear old text =====
    address_box.clear()
    time.sleep(2)

    # ===== Type new address =====
    address_box.send_keys("Lagbe na")
    time.sleep(2)

    save_button = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(text(), 'Save') or contains(text(), 'Update')]"
    )))
    time.sleep(2)
    save_button.click()
    time.sleep(2)


    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[contains(normalize-space(.), 'Profile')]"
    ))).click()

    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(normalize-space(.), 'Logout')]"
    ))).click()

    time.sleep(2)
    print("✅ Hoiche ")

finally:
    driver.quit()
