import requests
from bs4 import BeautifulSoup
from flask import Flask ,jsonify
import json
import os


app = Flask(__name__)
app.url_map.strict_slashes = False


def torrent(search):
    url = "https://1337x.to/search/"+search+"/1/"

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
        tp = tr.find_all('td',{'class':["size"]}) 
        date_find = tr.find_all('td',{'class':["coll-date"]})
        seeder_find =tr.find_all('td',{'class':["coll-2","seeds"]})
        leecher_find =tr.find_all('td',{'class':["coll-3" ,"leeches"]})

        for size,date,seeder,leecher in zip(tp,date_find,seeder_find,leecher_find):
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
    total_downloads_list = []
    last_checked_list = []
    

    for url_list in link_list:
        magnet_url_list_append = []

        magnet_req = requests.get(url_list,headers={
                    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'})
        new_soup = BeautifulSoup(magnet_req.content,'lxml')
        everything_data_list = []

        div = new_soup.find('div',class_='box-info-heading').text
        file_name.append(div)
        for span in new_soup.find_all('span'):
            if span.text != "":
                everything_data_list.append(span.text)

        total_downloads_list.append(everything_data_list[6])
        last_checked_list.append(everything_data_list[7])
        
        
        with open("source.txt",'w') as file:
            file.writelines(str(magnet_req.content))

        with open('source.txt','r+') as f:
            for line in f: 
                # reading each word         
                for word in line.split(): 
                    if 'magnet' in word:
                    # displaying the words            
                        magnet_url_list_append.append(word)
        magnet_url = magnet_url_list_append[0].split('"')[1]
        magnet_url_list.append(magnet_url)
    
    return file_name,file_size,link_list,date_list,seeder_list,leecher_list,magnet_url_list,total_downloads_list,last_checked_list

@app.route('/')
def home_page():
    return "Welcome"

@app.route('/<query>')
def home(query):

    file_name,file_size,link_list,date_list,seeder_list,leecher_list,magnet_url_list,total_downloads_list,last_checked_list = torrent(query)

    return jsonify([{'Name':file_name[index],
    'size':file_size[index],'url':link_list[index],
    'uploadDate': date_list[index],
    'seeders':seeder_list[index],
    'leechers': leecher_list[index],
    'magnet': magnet_url_list[index],
    'downloads':total_downloads_list[index],
    'lastChecked': last_checked_list[index]} 
    for index in range(len(file_name))])



if __name__ == "__main__":
    app.debug = True
    app.run(host"0.0.0.0",port=5000)
