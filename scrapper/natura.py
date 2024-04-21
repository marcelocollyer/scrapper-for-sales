from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from html2image import Html2Image
from telegram import Update
from telegram.ext import ContextTypes
import os
from datetime import datetime
import jinja2

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Processando...")
    print("webscrapper is running...")
    today = datetime.now()

    try:
        # Config driver        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1400")
        driver = webdriver.Chrome(options=options)

        # initializing jinja
        folder_path = os.getcwd()
        template_loader = jinja2.FileSystemLoader('.')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('templates/natura.html.j2')

        # Gets the url from the request
        url = get_url(update)
        driver.get(url)

        # scraps product image, url and title
        element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sticky-container"]/div[2]/div/div/div[1]/div[1]/div[2]')))
        element.screenshot(f'image-{today.timestamp()}.png')
        image_src = f'{folder_path}/image-{today.timestamp()}.png'
        productTitle = driver.find_element(By.XPATH, '//*[@id="sticky-container"]/div[2]/div/div/div[2]/div/h1').get_attribute('innerHTML')
        
        # if sp has been provided as parameter, no need to find the prices, otherwise...
        if ' sp' not in update.message.text[-3:]:
            element = driver.find_element(By.XPATH, '//*[@id="sticky-container"]/div[2]/div/div/div[2]/div/div[3]')
            element.screenshot(f'price-{today.timestamp()}.png')
            price_src = f'{folder_path}/price-{today.timestamp()}.png'

            xpath_product_price_before = '//*[@id="sticky-container"]/div[2]/div/div/div[2]/div/div[3]/div[1]/p'
            xpath_product_price = '//*[@id="sticky-container"]/div[2]/div/div/div[2]/div/div[3]/div[1]/div'
            xpath_payment = '//*[@id="sticky-container"]/div[2]/div/div/div[2]/div/div[3]/div[2]'

            productPriceBefore = get_element_text(driver, xpath_product_price_before)
            productPrice = get_element_text(driver, xpath_product_price)
            payment = get_element_text(driver, xpath_payment)

        # generates and sends to telegram the normal size image
        path = f'{today.timestamp()}.png'
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'price_src': price_src,
            'image_src': image_src, 
            'productTitle': productTitle,
            'background_img_name': folder_path + '/image/background', 
            'height': '1599'
        })
        print(html)
        hti.screenshot(html_str=html, save_as=path, size=(899, 1599))
        caption = f"<a href='{url}'>{url}</a>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=path,caption=caption,parse_mode='HTML',photo=open(path, "rb"))

        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'price_src': price_src,
            'image_src': image_src, 
            'productTitle': productTitle,
            'background_img_name': folder_path + '/image/background_small', 
            'height': '1166'
        })
        print(html)
        hti.screenshot(html_str=html, save_as=path, size=(899, 1166))
        caption = f"🛍️🛒{productTitle}\n\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{url}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=path,caption=caption,parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

    except Exception as error:
        print("Erro ao gerar imagem", error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Erro ao gerar imagem!")
    finally:
        deleteTempFiles(today.timestamp())
        driver.quit()

def get_url(update):
    try:
        url_parts = update.message.text.split()
        if len(url_parts) > 1:
            return url_parts[1]
        else:
            return ''
    except Exception as error:
        print("Error parsing URL: ", error)
        return ''       

def get_element_text(driver, xpath, label="element"):
    
    try:
        return driver.find_element(By.XPATH, xpath).text.replace('\n', '')
    except NoSuchElementException:
        print(f"Error: {label} not found.")
        return ''
    except WebDriverException as e:
        print(f"Error parsing {xpath}: {e}")
        return ''

def deleteTempFiles(date_time):
    if os.path.exists(f"{date_time}.png"):
        os.remove(f"{date_time}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"price-{date_time}.png"):
        os.remove(f"price-{date_time}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"image-{date_time}.png"):
        os.remove(f"image-{date_time}.png")
    else:
        print("The file does not exist")