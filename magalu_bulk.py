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

def deleteTempFiles(index):
    if os.path.exists(f"original-image-{index}.png"):
        os.remove(f"original-image-{index}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"image-{index}.png"):
        os.remove(f"image-{index}.png")
    else:
        print("The file does not exist")

async def sendDailyPromo(driver, update: Update, context: ContextTypes.DEFAULT_TYPE):

    folder_path = os.getcwd()
    driver.get('https://www.magazinevoce.com.br/magazinelojapexincha/selecao/ofertasdodia/?filters=review---4%2Bseller---magazineluiza')

    products = WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[2]/div/ul'))))
    WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.CLASS_NAME, 'text-button-cookie')))).click()

    # Find all product li elements within the ul list
    products = products.find_elements(By.TAG_NAME, 'li')

    # Extract details from each product
    for i, product in enumerate(products):
        link = product.find_element(By.TAG_NAME, 'a')
        product_url = link.get_attribute('href')
        original_image_path = f'original-image-{i+1}.png'
        product.screenshot(original_image_path)

        image_path = f'image-{i+1}.png'
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = getHTML(original_image_path, folder_path, 'background', '1599')
        hti.screenshot(html_str=html, save_as=image_path, size=(899, 1599))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"{image_path}",caption=f"<a href='{product_url}'>{product_url}</a>",parse_mode='HTML',photo=open(f"{image_path}", "rb"))    

        productTitle = product.find_element(By.CSS_SELECTOR, '[data-testid="product-title"]').text
        
        productPriceBefore = ''
        productPrice = ''
        payment = ''
        
        try:
            productPriceBefore = product.find_element(By.CSS_SELECTOR, '[data-testid="price-original"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing previous price ", error)
        try:                
            productPrice =  product.find_element(By.CSS_SELECTOR, '[data-testid="price-value"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing price ", error)    
        try:    
            payment = product.find_element(By.CSS_SELECTOR, '[data-testid="installment"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing payment methods ", error)

        html = getHTML(original_image_path,folder_path, 'background_small', '1166')
        hti.screenshot(html_str=html, save_as=image_path, size=(899, 1166))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=f"🛍️🛒{productTitle}\n\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{product_url}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>",parse_mode='HTML',photo=open(f"{image_path}", "rb"))
        
        deleteTempFiles(i+1)
        
        time.sleep(3)

def getHTML(image_path, folder_path, background_img_name, height):
    html = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Product Information</title>
            </head>
            <style>          
                .body {
                    margin: 0px;
                }
                        
                .internal-div {
                    margin: 0px 0px 0px 0px;
                    """+ f"""height: {height}px;
                    """+"""width: 899px;"""+ f"""
                    background-image: url('{folder_path}/{background_img_name}.jpg');"""+"""
                }

                .product-div {
                    padding: 150px 5px 5px 5px;
                    min-height: 680px;
                }

                .price-div {
                    
                    box-sizing: border-box;
                    color: rgb(15, 17, 17);
                    display: inline;
                    font-family: Arial, sans-serif;
                    font-size: 28px;
                    height: auto;
                    line-height: normal;
                    text-size-adjust: 100%;
                    width: auto;
                }

                .old-price-div {
                    text-align: center;
                    font-size: 25px;
                    margin: 0px 0px 0px 0px;
                    color: rgb(86, 89, 89);
                }

                .price {
                    text-align: center;
                    padding-left: 50px;
                }

                .old-price {
                    text-decoration: line-through;
                }
                
                .title {
                    margin-left: auto;
                    margin-right: auto;
                    text-align: center;
                    max-width: 650px;
                    font-family: serif;
                    font-size: 45px;
                    text-align: left;
                    color: #4a4a4a;
                    overflow: hidden;
                    display: -webkit-box;
                    -webkit-line-clamp: 4;
                    -webkit-box-orient: vertical;
                }

                .product-img {
                    /* Background pattern from Toptal Subtle Patterns */
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    max-width: 767px;
                    height: 945px;
                }

            </style>"""

    html += f"""
        <body class="body">
            <div class="internal-div">
            <div class="product-div">
                <img src="{folder_path}/{image_path}" class="product-img">
            </div>
            </div>
        </body>
    </html>"""        
    return html