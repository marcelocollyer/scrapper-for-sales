from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html2image import Html2Image
from telegram import Update
from telegram.ext import ContextTypes
import os
import time
from datetime import datetime
import jinja2

async def send_by_product_code(product_codes, driver, update: Update, context: ContextTypes.DEFAULT_TYPE):

    # initializing jinja
    folder_path = os.getcwd()
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('templates/magalu.html.j2')
    
    for code in product_codes:

        # Navigates to promotion website for each of the products
        url = os.environ.get("MAGALU_STORE_SEARCH_URL")
        template = jinja2.Template(url)
        url = template.render(productCode=code)
        driver.get(url)
        
        # Scrap all product information by taking a screenshot
        product = WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[3]/div/ul/li'))))
        
        link = product.find_element(By.TAG_NAME, 'a')
        product_url = link.get_attribute('href')
        original_image_path = f'original-image.png'
        product.screenshot(original_image_path)

        #loading template
        template_loader = jinja2.FileSystemLoader('.')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('templates/magalu_bulk.html.j2')

        # Sends the small background type image
        image_path = f'image.png'
        caption = f"<a href='{product_url}'>{product_url}</a>"
        data = {
            'image_path': folder_path + '/' + original_image_path,
            'height': '1599',
            'background_img_name': folder_path + '/image/background'
        }
        html = template.render(data)
        hti = Html2Image(custom_flags=['--no-sandbox'])
        hti.screenshot(html_str=html, save_as=image_path, size=(899, 1599))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"{image_path}",caption=caption,parse_mode='HTML',photo=open(f"{image_path}", "rb"))    

        # gather the product information
        productTitle = product.find_element(By.CSS_SELECTOR, '[data-testid="product-title"]').text
        productPriceBefore = get_element_text_or_innerhtml(product, '[data-testid="price-original"]')
        productPrice = get_element_text_or_innerhtml(product, '[data-testid="price-value"]')
        payment = get_element_text_or_innerhtml(product, '[data-testid="installment"]')

        # Set the photo and text content
        photo_url = f"{folder_path}/{image_path}"
        caption = f"🛍️🛒{productTitle}\n\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{product_url}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>"

        # Sends the normal background type image
        data = {
            'image_path': folder_path + '/' + original_image_path,
            'height': '1166',
            'width': '1166',
            'background_img_name': folder_path + '/image/background_small'
        }
        html = template.render(data)
        hti.screenshot(html_str=html, save_as=image_path, size=(1166, 1166))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=caption,parse_mode='HTML',photo=open(f"{image_path}", "rb"))
        
        # Clear out the temp files
        deleteTempFiles()
        
        # this avoids telegram from being flooded
        time.sleep(3)

def get_element_text_or_innerhtml(element, css_selector):
    try:
        return element.find_element(By.CSS_SELECTOR, css_selector).get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
    except Exception as error:
        print(f"Error parsing {css_selector}: {error}")
        return ''

def deleteTempFiles():
    if os.path.exists(f"original-image.png"):
        os.remove(f"original-image.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"image.png"):
        os.remove(f"image.png")
    else:
        print("The file does not exist")

def render_url_with_variable(instagram_business_account_id, url):
    # Define the template with the placeholder
    template_string = url

    # Create a Template object
    template = jinja2.Template(template_string)

    # Render the template with the actual Instagram Business Account ID
    rendered_url = template.render(instagram_business_account_id=instagram_business_account_id)

    return rendered_url        