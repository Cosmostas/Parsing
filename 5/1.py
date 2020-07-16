from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from pymongo import MongoClient


driver = webdriver.Chrome('Parsing/chromedriver.exe')
url = 'https://mail.ru/'

driver.get(url)


client = MongoClient('localhost', 27017)
db = client['mail_letter']


mail = db.mail
mail.drop({})

try:
    elem = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID,'mailbox:login'))
        )
    elem.send_keys('study.ai_172@mail.ru')
except:
    print("ERROR")

elem.send_keys(Keys.ENTER)

while True:
    try:
        elem = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.ID,'mailbox:password'))
            )
        elem.send_keys('NextPassword172')
        break
    except:
        print("ERROR")

elem.send_keys(Keys.ENTER)

letter_list = []

last_letter = None
while True:
    try:
        letters = WebDriverWait(driver,15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME,'llc'))
        )
        if letters[-1] == last_letter:
            break
        else:
            last_letter = letters[-1]

        
        for letter in letters:
            
            letter_data = {
                '_id' : hash(letter.get_attribute('href')),
                'sender': letter.find_element_by_class_name('ll-crpt').text,
                'departure_date': letter.find_element_by_class_name('llc__item_date').get_attribute('title'),
                'letter_theme': letter.find_element_by_class_name('ll-sj__normal').text,
                'href' :  letter.get_attribute('href')
            }

            mail.replace_one(letter_data, letter_data, upsert=True)

        actions = ActionChains(driver)
        actions.move_to_element(letters[-1])   #.key_down(Keys.CTRL).key_down(Keys.ENTER).key_up(Keys.Enter)
        actions.perform()
    except: 
        print("ERROR")
        break

for letter in mail.find({}):
    href = letter['href']
    driver.get(href)

    text_body = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'letter-body__body'))
    )
    letter['text'] = text_body.text

    mail.replace_one({'_id' : letter['_id']}, letter, upsert=True)
    


driver.quit()