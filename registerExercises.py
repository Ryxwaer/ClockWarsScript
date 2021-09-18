#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime, timedelta
import sys
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

##### CONFIG #################################################################
url = "https://wis.fit.vutbr.cz/FIT/st/course-sl.php.cs?id=781731&item=84898"
registerButtonName = "log_84901"
webDriverRefreshRate = 0.01
timeCorrection = 0
################################################################# CONFIG #####

url = url.split("/")
url = url[2:]
url = "/".join(url)

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://" + sys.argv[1] + ":" + sys.argv[2] + "@" + url)

expectedValue = "abcd";
if len(sys.argv) > 3:
    desiredTime = sys.argv[3]
else:
    desiredTime = "00:00"

time = datetime.strptime(desiredTime, "%M:%S")
time = time - timedelta(seconds=2)

desiredTime = time.strftime("%M:%S")

actualValue = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr/td[2]/div").text
wait = WebDriverWait(driver, 10, poll_frequency=webDriverRefreshRate)

maxIteration = int((2+timeCorrection)*10)
charList = ["#"]

for i in range(0, maxIteration):
    charList.append("#")

sleep(1)
while(1):
    wait.until_not(EC.text_to_be_present_in_element((By.XPATH, "/html/body/table[2]/tbody/tr/td[2]/div"), actualValue));
    actualValue = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr/td[2]/div").text
    print(" ", actualValue[-5:])
    if actualValue[-5:] == desiredTime:
        print(" almost thgere...")
        for i in range(maxIteration,0,-1):
            progresBar = "".join(charList[:i])
            print(f" {progresBar}" , end="\n", flush=True)
            sleep(0.1)
        break
print("\n*** is the time ***")

element = driver.find_element_by_name(registerButtonName)
if element.get_attribute("value") == "přihlásit":
    element.click()
    print("button with name ", registerButtonName, " was clicked immediatelly.")

for i in range(1, 10):
    driver.get("https://" + url)
    element = wait.until(EC.element_to_be_clickable((By.NAME, registerButtonName)))
    if element.get_attribute("value") == "přihlásit":
        element.click()
        print("button with name ", registerButtonName, " was clicked after refresh on iteration ", i)
