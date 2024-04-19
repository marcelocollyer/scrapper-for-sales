from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html2image import Html2Image
from telegram import Update
from telegram.ext import ContextTypes
import os
from datetime import datetime
      

def main():
    print("webscrapper is running...")

    options = Options()
    #options.add_argument('--headless')
    #options.add_argument('--no-sandbox')
    #options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1400")
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.magazineluiza.com.br/selecao/ofertasdodia/?filters=seller---magazineluiza%2Breview---4')

    products = WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[2]/div/ul'))))
    
    # Find all product li elements within the ul list
    products = products.find_elements(By.TAG_NAME, 'li')

    # Extract details from each product
    for i, product in enumerate(products):
        price_path = f'price-{i}.png'
        product.screenshot(price_path)
        sleep(0.5)

main()        