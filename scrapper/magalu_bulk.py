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
import requests
import json
import requests
import boto3
import jinja2

async def sendDailyPromo(driver, update: Update, context: ContextTypes.DEFAULT_TYPE):

    # initializing jinja
    folder_path = os.getcwd()
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('templates/magalu_bulk_template.html.j2')
    
    # Navigates to promotion website
    driver.get(os.environ.get('OFERTAS_URL'))
    
    # Scrap the product list
    products = WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.XPATH, '//*[@id="__next"]/div/main/section[4]/div[2]/div/ul'))))
    WebDriverWait(driver, 100).until(EC.presence_of_element_located(((By.CLASS_NAME, 'text-button-cookie')))).click()
    products = products.find_elements(By.TAG_NAME, 'li')

    # Extract details from each product
    for i, product in enumerate(products):
        link = product.find_element(By.TAG_NAME, 'a')
        product_url = link.get_attribute('href')
        original_image_path = f'original-image-{i+1}.png'
        product.screenshot(original_image_path)

        # Sends the small background type image
        image_path = f'image-{i+1}.png'
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
        
        # TODO uncomment this once IG business account gets created
        # Upload file to s3 as with public access and uses the public url to post on instagram stories
        #access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        #instagram_business_account_id = os.environ.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        #upload_file_to_s3(photo_url, 'dicemedice', 'story.jpg')
        #post_to_facebook(instagram_business_account_id, access_token, text, product_url)

        # Sends the normal background type image
        data = {
            'image_path': folder_path + '/' + original_image_path,
            'height': '1166',
            'background_img_name': folder_path + '/image/background_small'
        }
        html = template.render(data)
        hti.screenshot(html_str=html, save_as=image_path, size=(899, 1166))
        await context.bot.send_photo(chat_id=update.effective_chat.id,filename=f"magalu.png",caption=caption,parse_mode='HTML',photo=open(f"{image_path}", "rb"))
        
        # Clear out the temp files
        deleteTempFiles(i+1)
        
        # this avoids telegram from being flooded
        time.sleep(3)

def get_element_text_or_innerhtml(element, css_selector):
    try:
        return element.find_element(By.CSS_SELECTOR, css_selector).get_attribute('innerHTML').replace("<!-- -->", "").replace('&nbsp;','')
    except Exception as error:
        print(f"Error parsing {css_selector}: {error}")
        return ''

def post_to_facebook(instagram_business_account_id, access_token, text, product_url):
    
    # Construct the API request
    url = f"https://graph.facebook.com/v19.0/{instagram_business_account_id}/media"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    data = {
        "caption": text,
        "image_url": os.environ.get('S3_TEMP_IMAGE_PATH'),
        "media_type": "STORIES",
        "links": [
            {
                "url": product_url,
                "caption": "🛒 CLIQUE AQUI PARA COMPRAR"
            }
        ]
    }
    
    # Send the request
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Part A of the post successful!")
        
        # Get the creation ID from the previous response
        creation_id = json.loads(response.text)["id"]
        
        # Construct the API request for publishing the media
        url = f"https://graph.facebook.com/v19.0/{instagram_business_account_id}/media_publish"
        params = {"creation_id": creation_id}
        
        # Send the request
        response = requests.post(url, headers={"Authorization": f"Bearer {access_token}"}, params=params)
        
        if response.status_code == 200:
            print("Media published successfully!")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error: {response.text}")

def upload_file_to_s3(local_path, bucket_name, file_name):
    # Set up your AWS credentials
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    # Upload the file to S3
    with open(local_path, 'rb') as data:
        s3.put_object(Body=data, Bucket=bucket_name, Key=file_name)

    # Make the file publicly accessible
    s3.put_object_acl(Bucket=bucket_name, Key=file_name, ACL='public-read')

    # Print success message
    print(f"File uploaded successfully: {file_name}")   

def deleteTempFiles(index):
    if os.path.exists(f"original-image-{index}.png"):
        os.remove(f"original-image-{index}.png")
    else:
        print("The file does not exist")

    if os.path.exists(f"image-{index}.png"):
        os.remove(f"image-{index}.png")
    else:
        print("The file does not exist")