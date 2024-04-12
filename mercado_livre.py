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
        url = update.message.text.split()[1]
        driver.get(url)

        folder_path = os.getcwd().replace("\\", "\\\\")

        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/span[1]/figure/img')))
        element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div/div/span[1]/figure/img')
        element.screenshot(f'image-{today.timestamp()}.png')
        image_src = f'{folder_path}/image-{today.timestamp()}.png'

        element = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[3]/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[1]/div/div[2]/h1')
        productTitle = element.get_attribute('innerHTML')

        price_src = ''
        try:
            if 'sp' not in update.message.text:
                element = driver.find_element(By.CLASS_NAME, 'ui-pdp-price__main-container')
                element.screenshot(f'price-{today.timestamp()}.png')
                price_src = f'{folder_path}/price-{today.timestamp()}.png'
        except Exception as error:
            print("Error finding price", error)

        hti = Html2Image()
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
                    height: 1599px;
                    width: 899px;"""+ f"""
                    background-image: url("{folder_path}/background.jpg");"""+"""
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
                    max-width: 700px;
                    font-family: serif;
                    font-size: 45px;
                    text-align: left;
                    color: #4a4a4a;
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
                    max-width: 820px;
                }
            </style>"""

        image_tag = ''
        if price_src != '':
            image_tag = f"""<img src="{price_src}" class=product-img width="750px">"""

        html += f"""
            <body class="body">
                <div class="internal-div">
                <div class="product-div">
                    <img src="{image_src}" alt="Product Image" class=product-img height="500">
                    <h1 class="title">{productTitle}</h1>
                </div>
                <div class="price-div">
                    <p class="price">{image_tag}</p>  
                </div>
                </div>
            </body>
        </html>"""

        print(html)
        # screenshot an HTML string (css is optional)
        hti = Html2Image(custom_flags=['--no-sandbox'])
        hti.screenshot(html_str=html, save_as=f'{today.timestamp()}.png', size=(899, 1599))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"{today}.png",photo=open(f"{folder_path}/{today.timestamp()}.png", "rb"))
    except Exception as error:
        print("Erro ao gerar imagem", error)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Erro ao gerar imagem!")
    finally:
        deleteTempFiles(today.timestamp())
        driver.quit()