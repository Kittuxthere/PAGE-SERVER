from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Messenger Login Credentials (Manually Enter या Session Use कर)
EMAIL = "your-email@gmail.com"
PASSWORD = "your-facebook-password"

# जिस बंदे को मैसेज भेजना है उसका नाम
TARGET_NAME = "Target Friend Name"

# जो मैसेज भेजना है
MESSAGE_TEXT = "Hello, this is an E2EE message sent via automation!"

# Chrome WebDriver सेटअप
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")  # Full screen
options.add_argument("--disable-notifications")  # Disable popups

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 1. Facebook Messenger Open करो
driver.get("https://www.messenger.com/")

# 2. Login करो (अगर Cookies नहीं Use कर रहे हो)
time.sleep(3)
email_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.ID, "pass")

email_input.send_keys(EMAIL)
password_input.send_keys(PASSWORD)
password_input.send_keys(Keys.RETURN)

# 3. Messenger Chats Load होने दो
time.sleep(5)

# 4. Search for the Target User (E2EE Chat)
search_box = driver.find_element(By.XPATH, '//input[@type="search"]')
search_box.send_keys(TARGET_NAME)
time.sleep(3)  # Wait for search results

# 5. Click on the Target Chat
target_chat = driver.find_element(By.XPATH, f"//span[text()='{TARGET_NAME}']")
target_chat.click()
time.sleep(3)

# 6. Send Message
message_box = driver.find_element(By.XPATH, '//div[@aria-label="Type a message…"]')
message_box.send_keys(MESSAGE_TEXT)
message_box.send_keys(Keys.RETURN)

print("✅ Message Sent Successfully in E2EE Chat!")

# 7. Close Browser
time.sleep(2)
driver.quit()
