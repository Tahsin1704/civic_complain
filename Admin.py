from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

try:
    driver.get("http://127.0.0.1:8000/")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR,
        "a.btn.btn-primary.btn-custom, button.btn.btn-primary.btn-custom"
    ))).click()
    time.sleep(2)
    driver.get("http://127.0.0.1:8000/login/")
    driver.find_element(By.NAME, "username").send_keys("shahriaamin@gmail.com")
    time.sleep(2)
    driver.find_element(By.NAME, "password").send_keys("shahria123")
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@class='btn btn-primary w-100 mt-2']").click()
    time.sleep(2)
    driver.find_element(By.NAME, "q").send_keys("TASK-0021")
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@class='btn btn-primary']").click()
    time.sleep(2)
    back = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[@href='/dashboard/admin/' and contains(@class,'btn-secondary')]"
    )))
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", back)
    back.click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[contains(normalize-space(.), 'Workers')]" 
    ))).click()
    time.sleep(2)
    tahsin_row = wait.until(EC.presence_of_element_located((
    By.XPATH, "//tr[td[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sajid@gmail.com')]]"
    )))

    update_button = tahsin_row.find_element(By.XPATH, ".//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'update')]")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", update_button)
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



    # ===== (Optional) Click Save or Submit button =====
    # Adjust XPath or class if your form button differs
    save_button = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(text(), 'Save') or contains(text(), 'Update')]"
    )))
    time.sleep(2)
    save_button.click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[contains(normalize-space(.), 'Add Worker')]"
    ))).click()
    time.sleep(2)
    # ====== Fill Worker Details ======

    # Email
    wait.until(EC.presence_of_element_located((By.ID, "id_email"))).send_keys("ali@gmail.com")
    time.sleep(2)
    # Password
    driver.find_element(By.ID, "id_password").send_keys("alibaba12345")
    time.sleep(2)
    # First Name
    driver.find_element(By.ID, "id_first_name").send_keys("Ali")
    time.sleep(2)
    # Last Name
    driver.find_element(By.ID, "id_last_name").send_keys("Baba")
    time.sleep(2)
    # Phone
    driver.find_element(By.ID, "id_phone").send_keys("01742347882")
    time.sleep(2)
    # Address
    driver.find_element(By.ID, "id_address").send_keys("Farmgate")
    time.sleep(2)
    # Skills
    driver.find_element(By.ID, "id_skills").send_keys("Electrical Maintenance")
    time.sleep(2)
    
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(normalize-space(.), 'Create Worker')]"
    ))).click()

    print("✅ New Worker added successfully.")

    time.sleep(3)
    wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//a[normalize-space()='Delete' and contains(@href,'/workers/') and contains(@href,'/delete/')]"))
    ).click()
    time.sleep(3)

    wait.until(EC.visibility_of_element_located((By.ID, "reason"))).send_keys("faltu")
    time.sleep(3)
    wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//button[@type='submit' and contains(normalize-space(),'Delete Worker')]")
    )).click()
    time.sleep(3)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//a[contains(normalize-space(.), 'Citizens')]"
    ))).click()
    time.sleep(2)
    wait.until(EC.element_to_be_clickable((
    By.XPATH, "//button[contains(normalize-space(.), 'Logout')]"
    ))).click()
    time.sleep(2)
    print("Done")
finally:
    driver.quit()
