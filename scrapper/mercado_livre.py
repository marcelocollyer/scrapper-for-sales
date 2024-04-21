from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
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
        template = template_env.get_template('templates/mercado_livre.html.j2')

        # Gets the url from the request
        url = get_url(update)
        driver.get(url)
        driver.refresh()

        # scraps product image, url and title
        element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/span[1]/figure/img')))
        element.screenshot(f'image-{today.timestamp()}.png')
        image_src = f'{folder_path}/image-{today.timestamp()}.png'
        productTitle = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/h1').get_attribute('innerHTML')
        
        if ' sp' not in update.message.text[-3:]:
            element = driver.find_element(By.CLASS_NAME, 'ui-pdp-price__main-container')
            element.screenshot(f'price-{today.timestamp()}.png')
            price_src = f'{folder_path}/price-{today.timestamp()}.png'

            locator_product_price_before = '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[3]/div[1]/span/s'
            locator_product_price = '//*[@id="ui-pdp-main-container"]/div[1]/div/div[1]/div[2]/div[3]/div[1]/div[1]/span/span'
            locator_payment = 'ui-pdp-price__subtitles'

            # Retrieve element texts
            productPriceBefore = find_element(driver, locator_product_price_before)
            productPrice = find_element(driver, locator_product_price)
            payment = find_element(driver, locator_payment, By.CLASS_NAME)          

        # path for the final image
        path = f'{today.timestamp()}.png'
        
        # generates and sends to telegram the normal size image
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'folder_path': folder_path,
            'image_src': image_src,
            'price_src': price_src,
            'productTitle': productTitle,
            'height': '1599',
            'background_img_name': 'image/background'
        })  
        print(html)
        hti.screenshot(html_str=html, save_as=path, size=(899, 1599))
        caption = f"<a href='{url}'>{url}</a>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=path,caption=caption,parse_mode='HTML',photo=open(f"{folder_path}/{path}", "rb"))

        # generates and sends to telegram the small size image
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'folder_path': folder_path,
            'image_src': image_src,
            'price_src': price_src,
            'productTitle': productTitle,
            'height': '1166',
            'background_img_name': 'image/background_small'
        })
        print(html)
        hti.screenshot(html_str=html, save_as=path, size=(899, 1166))
        caption = f"🛍️🛒{productTitle}\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{url}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=caption,parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

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
    
def find_element(driver, locator, locator_type=By.XPATH):
    
    try:
        element = driver.find_element(locator_type, locator)
        return element.text.replace('\n', '')
    except NoSuchElementException as e:
        print(f"Error parsing element {locator}: {e}")
        return ''
    except Exception as error:
        print(f"Unhandled error with element {locator}: {error}")
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