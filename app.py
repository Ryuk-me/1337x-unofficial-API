import requests
from bs4 import BeautifulSoup
from flask import Flask ,jsonify
import json

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

    for tr in table_rows:
        td = tr.find_all('td',{'class':["coll-1","name"]})
        tp = tr.find_all('td',{'class':["size"]}) 
        # row = [i.text for i in td]
        for name,size in zip(td,tp):
            file_name.append(name.text)
            if "GB" in size.text:
                size = size.text.split(' ')[0]+" GB"
                file_size.append(size)
            else:
                size = size.text.split(' ')[0]+" MB"
                file_size.append(size)


    table = soup.find('table')
    table_rows = table.find_all('tr')
    link_list = []

    for a in soup.find_all('a', href=True, text=True):
        link_text = str(a['href'])
        if link_text.startswith("/torrent"):
            link_text = "https://1337x.to"+link_text
            link_list.append(link_text)

    return file_name,file_size,link_list

@app.route('/')
def home_page():
    return "Welcome"

@app.route('/<query>')
def home(query):

    file_name,file_size,link_list = torrent(query)

    #all_data = [{'name':file_name[index],'size':file_size[index],'url':link_list[index]} for index in range(len(file_name))]

    return jsonify([{'name':file_name[index],'size':file_size[index],'url':link_list[index]} for index in range(len(file_name))])



if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0",port=5000)
