from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html2image import Html2Image
from telegram import Update
from telegram.ext import ContextTypes
import os
import jinja2
from datetime import datetime
from scrapper import magalu_bulk

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

        # This command is handled separated 
        if update.message.text.startswith(("/mag ofertas")):
            await magalu_bulk.sendDailyPromo(driver, update, context)
            return 

        # initializing jinja
        folder_path = os.getcwd()
        template_loader = jinja2.FileSystemLoader('.')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('templates/magalu_template.html.j2')

        # Gets the url from the request
        url = get_url(update)
        driver.get(url)

        # gets the product code and high resolution image path
        productCode = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[2]/div[2]/span/span[1]').text.split(' ')[1]
        imageHighRes = driver.find_element(By.CSS_SELECTOR, '[data-testid="image-selected-thumbnail"]').get_attribute('src')
        
        # navigates to the search page and uses product code to search
        searchUrl = os.environ.get('MAGALU_STORE_SEARCH_URL')
        searchUrl = replace_text_in_template(searchUrl, productCode)
        driver.get(searchUrl)

        # scraps product url and title
        image_path = imageHighRes
        productUrl = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[3]/div/ul/li/a').get_attribute('href')
        productTitle = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[3]/div/ul/li/a/div[3]/h2').text
        
        # if sp has been provided as parameter, no need to find the prices, otherwise...
        if ' sp' not in update.message.text[-3:]:
            # Continue to extract values
            productPriceBefore = get_value(driver, '[data-testid="price-original"]')
            productPrice = get_value(driver, '[data-testid="price-value"]')
            payment = get_value(driver, '[data-testid="installment"]')
        
        # Takes a screenshot of the price information
        price_path = capture_prices(driver, today)
        
        # path for the final image
        path = f'{today.timestamp()}.png'
        
        # generates and sends to telegram the normal size image
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'image_path': image_path,
            'price_path': folder_path + '/' + price_path,
            'height': '1599',
            'background_img_name': folder_path + '/image/background'
        })
        hti.screenshot(html_str=html, save_as=path, size=(899, 1599))
        caption = f"<a href='{productUrl}'>{productUrl}</a>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=caption,parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

        # generates and sends to telegram the small size image
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = template.render({
            'image_path': image_path,
            'price_path': folder_path + '/' + price_path,
            'height': '1166',
            'background_img_name': folder_path + '/image/background_small'
        })
        hti.screenshot(html_str=html, save_as=path, size=(899, 1166))
        caption = f"🛍️🛒{productTitle}\n\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{productUrl}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>"
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=caption,parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

    except Exception as error:
        print("Erro ao gerar imagem", error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Erro ao gerar imagem!")
    finally:
        deleteTempFiles(today.timestamp())
        driver.quit()

def capture_prices(driver, today):
    price_path = ''
    try:
        pricesElement = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-card-content"]')
        price_path = f"prices-{today.timestamp()}.png"
        pricesElement.screenshot(price_path)
    except Exception as error:
        print("Error parsing prices ", error)        
    return price_path    

def get_value(driver, css_selector):
    try:
        value = driver.find_element(By.CSS_SELECTOR, css_selector).get_attribute('innerHTML')
        return value.replace("<!-- -->", "").replace('&nbsp;','')
    except Exception as error:
        print(f"Error parsing {css_selector}: {error}")
        return ''

def replace_text_in_template(template_string, replacement_text):
    template = jinja2.Template(template_string)
    return template.render(productCode=replacement_text)

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

def deleteTempFiles(date_time):
    if os.path.exists(f"{date_time}.png"):
        os.remove(f"{date_time}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"prices-{date_time}.png"):
        os.remove(f"prices-{date_time}.png")
    else:
        print("The file does not exist") 