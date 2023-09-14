from flask import Flask, redirect, url_for, render_template, request
import logging
import requests
from bs4 import BeautifulSoup
import os
import pymongo

logging.basicConfig(filename="scraper.log",
                    level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/retrieve', methods=['GET','POST'])
def retrieve_images():
    try:
        if(request.method=='POST'):
            query = request.form['content']
            logging.info(query)
            save_dir = 'images/'
            if(not os.path.exists(save_dir)):
                os.makedirs(save_dir)

            url = f"https://www.google.com/search?q={query}&tbm=isch&ved=2ahUKEwiTtsuG0KeBAxUkoekKHcYeAcEQ2-cCegQIABAA&oq=chandrayaan+3&gs_lcp=CgNpbWcQAzIECAAQAzILCAAQgAQQsQMQgwEyCwgAEIAEELEDEIMBMgQIABADMgQIABADMgQIABADMgQIABADMgQIABADMgQIABADMgQIABADOg0IABCKBRCxAxCDARBDOgQIABAeOgUIABCABDoGCAAQBxAeUNECWJ0MYNcPaAFwAHgAgAGzAYgBlgWSAQMwLjSYAQCgAQGqAQtnd3Mtd2l6LWltZ8ABAQ&sclient=img&ei=EbABZdPpDaTCpgfGvYSIDA&bih=656&biw=1294&client=ubuntu&hs=uw8"
            response = requests.get(url)
            bs = BeautifulSoup(response.content, 'html.parser')
            img_tags = bs.find_all('img')
            del img_tags[0]
            list_images = []
            for idx, image_tag in enumerate(img_tags):
                img_url = image_tag['src']
                img_data = requests.get(img_url).content
                mydict = {'index':idx, "image_data":img_data}
                list_images.append(mydict)
                with open(os.path.join(save_dir, f"{query}_{img_tags.index(image_tag)}.jpg"), 'wb') as f:  # wb is write bytes
                    f.write(img_data)
            client = pymongo.MongoClient(
                "mongodb+srv://detiprudvi:yyMhq1HiJxCYUF4k@cluster0.ufdzcre.mongodb.net/?retryWrites=true&w=majority")
            logging.info(client.test)
            db = client['ImageScraping']
            retrieve_col = db['image_data']
            retrieve_col.insert_many(list_images)
        return "Images loaded"
    except Exception as e:
        logging.exception(e)
        return "something went wrong"

    else:
        return render_template('index.html')


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)