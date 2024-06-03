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
import requests
import json
import xml.etree.ElementTree as ET
import re
import os

##### CONFIG #################################################################
url = "https://wis.fit.vutbr.cz/FIT/st/course-sl.php.cs?id=781735&item=85325"
registerButtonName = "log_85353"
webDriverRefreshRate = 0.01
timeCorrection = -0.3
requestTimeout = 1
login_user="xpolic05"
login_pass="xxxxxxxx"
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

start = 0
end = 0

while(1):
    wait.until_not(EC.text_to_be_present_in_element((By.XPATH, "/html/body/table[2]/tbody/tr/td[2]/div"), actualValue));
    actualValue = driver.find_element_by_xpath("/html/body/table[2]/tbody/tr/td[2]/div").text
    print(" ", actualValue[-5:])
    if actualValue[-5:] == desiredTime:
        start = (datetime.now().minute * 60000000) + datetime.now().microsecond + datetime.now().second * 1000000
        end = start + ((2 + timeCorrection) * 1000000)
        print(" almost thgere...")
        break

y = json.dumps(driver.get_cookies())
parsed = json.loads(y)
cookies = ""
for record in reversed(parsed):
    if (record['name'] == "csltoken"):
        cookies = record['name'] + "=" + record['value']

item = driver.find_element_by_name('item').get_attribute("value")
ident = driver.find_element_by_name('id').get_attribute("value")
token = driver.find_element_by_name('token').get_attribute("value")

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'sec-ch-ua-platform': '"Linux"',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://wis.fit.vutbr.cz/FIT/st/course-sl.php.cs?id=' + ident + '&item=' + item,
    'Accept-Language': 'en-US,en;q=0.9',
    'Cookie': cookies
}

counter = 0
actualMS = 0
while actualMS < end:
    actualMS = datetime.now().microsecond
    actualMS += datetime.now().second * 1000000
    actualMS += datetime.now().minute * 60000000
    if (counter == 0):
        print("waiting for %d microseconds  " %(end - actualMS), end="", flush=True)
    if(counter % 10000 == 0):
        print("#", end="", flush=True)
    if(counter % 500000 == 0):
        print("#", flush=True)
    counter += 1

print("\nwaiting counter: %d iterations" %counter)
counter = 0
start = (datetime.now().minute * 60000000) + datetime.now().microsecond + datetime.now().second * 1000000
while ((datetime.now().minute * 60000000) + datetime.now().microsecond + datetime.now().second * 1000000) - start < 500000:
    try:
        counter += 1
        r = requests.get(f'https://{login_user}:{login_pass}@wis.fit.vutbr.cz/FIT/st/course-sl.php.cs?xml=' + token + '&id=' + ident + '&log_85353=xml', headers=headers, timeout=requestTimeout)
        responseXml = ET.fromstring(r.text)
        response = responseXml.find('.//item[@id="' + registerButtonName[4:] + '"]').text
        value = re.search(r'value="(\w+)"', response)
        value = value.group(0)
        if (value != 'value="přihlásit"'):
            break
    except requests.exceptions.ReadTimeout:
        pass
    except Exception as e:
        print(e)
        break
print("requests sent counter: %d" %counter)

"""
# Old code with click() implementation: NOT EXECUTED

element = driver.find_element_by_name(registerButtonName)
if element.get_attribute("value") == "přihlásit":
    element.click()
else:
    print("button with name ", registerButtonName, " was clicked immediatelly.")
    exit(0)

for i in range(1, 100):
    print("iteration: ", i)
    elementW = wait.until(EC.element_to_be_clickable((By.NAME, registerButtonName)))
    if elementW.get_attribute("value") == "přihlásit":
        elementW.click()
    else:
        print("button with name ", registerButtonName, " was clicked immediatelly.")
        exit(0)



print("refreshing page...")

for i in range(1, 10):
    driver.get("https://" + url)
    element = wait.until(EC.element_to_be_clickable((By.NAME, registerButtonName)))
    if element.get_attribute("value") == "přihlásit":
        element.click()
    else:
        print("button with name ", registerButtonName, " was clicked after refresh on iteration ", i)
        exit(0)
"""