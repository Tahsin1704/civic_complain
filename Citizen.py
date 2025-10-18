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

    wait.until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys("aliftalha@gmail.com")
    wait.until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys("aliftalha12345")
    time.sleep(2)
    
    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
    ).click()
    time.sleep(2)

    submit_button = driver.find_element(By.XPATH, "//a[contains(., 'Submit New Complaint')]")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
    time.sleep(2)
    submit_button.click()
    time.sleep(2)

    wait.until(EC.visibility_of_element_located((By.NAME, "title"))).send_keys("Electric Problrm")
    wait.until(EC.visibility_of_element_located((By.NAME, "description"))).send_keys("Tripped circuit")
    wait.until(EC.visibility_of_element_located((By.NAME, "category"))).send_keys("Electricity")
    wait.until(EC.visibility_of_element_located((By.NAME, "location"))).send_keys("Mohammadpur")
    wait.until(EC.visibility_of_element_located((By.NAME, "instructions"))).send_keys("Solve it")
    wait.until(EC.visibility_of_element_located((By.NAME, "estimated_time"))).send_keys("Oct 17, 2025")
    time.sleep(2)
    submit_btn = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class,'btn-success')]").click()

    time.sleep(2)
    view_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/tasks/106/detail/' and contains(text(), 'View')]")
    ))

    # Scroll to it and click
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", view_button)
    time.sleep(2)
    view_button.click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[contains(normalize-space(.), 'Profile')]"
    ))).click()

    time.sleep(2)
    update_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[@href='/profile/update/' and contains(text(), 'Update Profile')]")
))

# Scroll to the button and click it
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_button)
    time.sleep(2)
    update_button.click()
    time.sleep(2)

    address_box = wait.until(EC.presence_of_element_located((By.ID, "id_address")))

    # ===== Clear old text =====
    address_box.clear()
    time.sleep(2)

    # ===== Type new address =====
    address_box.send_keys("Noakhali")
    time.sleep(2)

    save_button = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(text(), 'Save') or contains(text(), 'Update')]"
    )))
    time.sleep(2)
    save_button.click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(normalize-space(.), 'Logout')]"
    ))).click()
    time.sleep(2)

finally:
    driver.quit()
