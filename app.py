from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import cv2
import matplotlib.pyplot as plt
import pytesseract
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import urllib.request
import time
import sys
import pandas as pd
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "footeuse"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_image(filename):
    return pytesseract.image_to_string(cv2.imread('static/uploads/'+ filename))

def web_upload(image_name):
    site = 'https://www.google.com/search?tbm=isch&q='+image_name
    chromeDriverPath = r'C:\Windows\chromedriver.exe'
    s = Service('C:\Windows\chromedriver.exe')
    driver = webdriver.Chrome(service=s)

    #passing site url
    driver.get(site)

    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")

    #parsing
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #closing web browser
    driver.close()

    #scraping image urls with the help of image tag and class used for images
    img_tags = soup.find_all("img", class_="rg_i", limit=1)


    count = 0
    try:
        #passing image urls one by one and downloading
        web_image_path = str(count)+".jpg"
        urllib.request.urlretrieve(img_tags[0]['src'], "static/uploads/"+str(count)+".jpg")
        count+=1
        print("Number of images downloaded = "+str(count),end='\r')
    except Exception as e:
        pass

    return web_image_path



@app.route('/')
def home():
	return render_template('index.html')



@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        textImage = read_image(filename)
        web_image = web_upload(textImage)
        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename = filename, textImage = textImage, web_image = web_image)
    else:
        flash('Allowed extensions: png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run(debug=True)


