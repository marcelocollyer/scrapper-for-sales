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
import magalu_bulk

def deleteTempFiles(date_time):
    if os.path.exists(f"{date_time}.png"):
        os.remove(f"{date_time}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"product-{date_time}.png"):
        os.remove(f"product-{date_time}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"prices-{date_time}.png"):
        os.remove(f"prices-{date_time}.png")
    else:
        print("The file does not exist")        

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Processando...")
    print("webscrapper is running...")
    today = datetime.now()

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1400")
        driver = webdriver.Chrome(options=options)

        if update.message.text.startswith(("/mag ofertas")):
            await magalu_bulk.sendDailyPromo(driver, update, context)
            return 

        url = update.message.text.split()[1]
        driver.get(url)

        folder_path = os.getcwd()

        productCode = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[2]/div[2]/span/span[1]').text.split(' ')[1]
        imageHighRes = driver.find_element(By.CSS_SELECTOR, '[data-testid="image-selected-thumbnail"]').get_attribute('src')
        
        driver.get(f"https://www.magazinevoce.com.br/magazinelojapexincha/busca/{productCode}/")

        image_path = imageHighRes
        
        productUrl = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[3]/div/ul/li/a').get_attribute('href')
        productTitle = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[3]/div/ul/li/a/div[3]/h2').text
        
        productPriceBefore = ''
        productPrice = ''
        payment = ''
        price_path = ''
        
        try:
            productPriceBefore = driver.find_element(By.CSS_SELECTOR, '[data-testid="price-original"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing previous price ", error)
        try:                
            productPrice =  driver.find_element(By.CSS_SELECTOR, '[data-testid="price-value"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing price ", error)    
        try:    
            payment = driver.find_element(By.CSS_SELECTOR, '[data-testid="installment"]').get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
        except Exception as error:
            print("Error parsing payment methods ", error)                
        try:    
            pricesElement = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-card-content"]')
            price_path = f'prices-{today.timestamp()}.png'
            pricesElement.screenshot(price_path)
        except Exception as error:
            print("Error parsing prices ", error)
        
        folder_path = folder_path.replace("\\", "\\\\")

        path = f'{today.timestamp()}.png'
        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = getHTML(image_path, price_path, folder_path, 'background', '1599')
        hti.screenshot(html_str=html, save_as=path, size=(899, 1599))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=f"<a href='{productUrl}'>{productUrl}</a>",parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

        hti = Html2Image(custom_flags=['--no-sandbox'])
        html = getHTML(image_path,price_path,folder_path, 'background_small', '1166')
        hti.screenshot(html_str=html, save_as=path, size=(899, 1166))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=f"🛍️🛒{productTitle}\n\n<s>{productPriceBefore}</s>\n{productPrice}🚨🚨🔥😱🏃🏻‍♀️\n💳 {payment}\n\n<a href='{productUrl}'>🛒 CLIQUE AQUI PARA COMPRAR</a>\n\n<i>*Promoção sujeita a alteração a qualquer momento</i>",parse_mode='HTML',photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))

    except Exception as error:
        print("Erro ao gerar imagem", error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Erro ao gerar imagem!")
    finally:
        deleteTempFiles(today.timestamp())
        driver.quit()

def getHTML(image_path, price_path, folder_path, background_img_name, height):
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
                    height: 545px;
                }

                .price-img {
                    /* Background pattern from Toptal Subtle Patterns */
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    max-width: 767px;
                    padding-top: 25px;
                    height: 400px;
                }
            </style>"""

    html += f"""
        <body class="body">
            <div class="internal-div">
            <div class="product-div">
                <img src="{image_path}" class="product-img">
                <img src="{folder_path}/{price_path}" class="price-img">
            </div>
            </div>
        </body>
    </html>"""        
    return html

