import requests
from bs4 import BeautifulSoup
from flask import Flask ,jsonify
import json
import os
from selenium import webdriver
from time import sleep


app = Flask(__name__)
app.url_map.strict_slashes = False


def torrent(search):
    url = "https://1337x.to/search/"+search+"/1/"


    hrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


    res = requests.get(url,headers={
                    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'})
                
    soup = BeautifulSoup(res.content,'lxml')

    table = soup.find('table')
    table_rows = table.find_all('tr')

    file_name = []
    file_size = []
    date_list = []
    seeder_list = []
    leecher_list =[]

    for tr in table_rows:
        td = tr.find_all('td',{'class':["coll-1","name"]})
        tp = tr.find_all('td',{'class':["size"]}) 
        date_find = tr.find_all('td',{'class':["coll-date"]})
        seeder_find =tr.find_all('td',{'class':["coll-2","seeds"]})
        leecher_find =tr.find_all('td',{'class':["coll-3" ,"leeches"]})

        for name,size,date,seeder,leecher in zip(td,tp,date_find,seeder_find,leecher_find):
            file_name.append(name.text)
            date_list.append(date.text)
            seeder_list.append(seeder.text)
            leecher_list.append(leecher.text)
            if "GB" in size.text:
                size = size.text.split(' ')[0]+" GB"
                file_size.append(size)
            else:
                size = size.text.split(' ')[0]+" MB"
                file_size.append(size)


    link_list = []

    for a in soup.find_all('a', href=True, text=True):
        link_text = str(a['href'])
        if link_text.startswith("/torrent"):
            link_text = "https://1337x.to"+link_text
            link_list.append(link_text)
    magnet_url_list = []

    for url_list in link_list:
        # print(url_list)
        url_list = "https://1337x.to"+url_list
        # magnet_req = requests.get(url_list,headers={
        #             'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'})
        print('hello')
        driver.get(url_list)
        sleep(5)
        magnet_req = driver.find_element_by_xpath("/html/body/main/div/div/div/div[2]/div[1]/ul[1]/li[1]/a")
        magnet_url_list.append(magnet_req.text)

    return file_name,file_size,link_list,date_list,seeder_list,leecher_list,magnet_url_list

@app.route('/')
def home_page():
    return "Welcome"

@app.route('/<query>')
def home(query):

    file_name,file_size,link_list,date_list,seeder_list,leecher_list,magnet_url_list = torrent(query)

    return jsonify([{'Name':file_name[index],'size':file_size[index],'url':link_list[index],'date': date_list[index],'seeders':seeder_list[index],'leechers': leecher_list[index],'magnet': magnet_url_list[index]} for index in range(len(file_name))])



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
