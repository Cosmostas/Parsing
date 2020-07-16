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

def insert_into_collection(collection, data):
    for job in data:
        collection.update(job, {'upsert' : True})

chrome_options = Options()
chrome_options.add_argument('start-maximized')  #--headless

driver = webdriver.Chrome('Parsing/chromedriver.exe',options=chrome_options)
url = 'https://www.mvideo.ru/'

driver.get(url)


client = MongoClient('localhost', 27017)
db = client['mvideo']


top_product = db.top_product
top_product.drop({})

try:
    elem = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"(//div[@data-init= 'gtm-push-products'])[2]"))
        )
    
    pages_list = elem.find_element_by_class_name('carousel-paging').find_elements_by_css_selector('a')

except:
    print("ERROR")

products = []

for i in range(len(pages_list)):
    time.sleep(1.5)
    elem = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"(//div[@data-init= 'gtm-push-products'])[2]"))
        )
    time.sleep(0.5)
    elem.find_element_by_class_name('carousel-paging').find_elements_by_css_selector('a')[i].click()
    time.sleep(0.5)
    product_list = elem.find_elements_by_css_selector('li')

    for product in product_list:
        product_data = {
            '_id' : hash(product.find_element_by_css_selector('h4').find_element_by_css_selector('a').get_attribute('href')),
            'name' :  product.find_element_by_css_selector('h4').text,
            'href' : product.find_element_by_css_selector('h4').find_element_by_css_selector('a').get_attribute('href'),
            'price' : product.find_element_by_class_name('c-product-tile__checkout-section').find_element_by_class_name('c-pdp-price__current').text[:-1],
        }
        if product_data['name'] == '':
            pass
        else:
            top_product.replace_one(product_data, product_data, upsert=True)

driver.quit()