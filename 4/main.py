import pprint as pprint
from lxml import html
import datetime
import requests
from pymongo import MongoClient
import hashlib

def parse_yandex_infoblock(infoblock):
    months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    is_old_post = False
    
    for month in months:
        if month in infoblock:
            is_old_post = True
            break
    
    if is_old_post:
        pos = infoblock.find(month)
        resource = infoblock[:pos - 4]
        date = infoblock[pos - 3:]
    elif infoblock.find('вчера') > -1:
        pos = infoblock.find('вчера')
        comp_date = datetime.datetime.now()

        month = months[comp_date.month]

        day = comp_date.day - 1 
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        
        resource = infoblock[:pos - 1]
        date = infoblock[pos:]
        date.replace("вчера", day + ' ' + month)
        
    else:
        pos = len(infoblock) - 5
        comp_date = datetime.datetime.now()

        month = months[comp_date.month]

        day = comp_date.day 
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        resource = infoblock[:pos - 1]
        date = infoblock[pos:]
        date = day + " " + month + " " + date
    return resource, date

def parse_yandex_id(href):
    digits = '0123456789'
    first_pos = href.find('persistent_id') + 14
    
    for i in range (first_pos, len(href)):
        if(href[i] not in digits):
            last_pos = i
            break
    return href[first_pos:last_pos]
        
def parse_yandex():
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
            'Accept':'*/*'}

    link = 'https://yandex.ru/news/'

    response = requests.get(link, headers = header)

    dom = html.fromstring(response.text)

    main_path = "//div[@aria-labelledby = 'computers']//td[@class = 'stories-set__item']"
    news_blocks = dom.xpath(main_path)
    
    news_list = []
    for news_block in news_blocks:
        news = {}
        
        name = news_block.xpath(".//h2[@class = 'story__title']/a/text()")[0]
        href = news_block.xpath(".//h2[@class = 'story__title']/a/@href")[0]

        infoblock = news_block.xpath(".//div[@class = 'story__date']/text()")[0]
        resource, date = parse_yandex_infoblock(infoblock)

        _id = parse_yandex_id(href)

        news = {
            '_id' : _id,
            'name' : name,
            'href' : href,
            'resource' : resource,
            'date' : date
        }

        news_list.append(news)
    
    return news_list

def parse_mail_id(href):
    pos = href.find("politics/")
    _id = href[pos + 9 : -1]
    return _id

def parse_mail():
    
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
            'Accept':'*/*'}

    link = 'https://news.mail.ru/'

    response = requests.get(link, headers = header)

    dom = html.fromstring(response.text)

    main_path = "(//div[@class = 'cols__wrapper']//div[@class = 'cols__inner'])[3]"
    news_blocks = dom.xpath(main_path)
    
    name_list = (news_blocks[0].xpath(".//a/span/text()"))[1:]
    href_list = (news_blocks[0].xpath(".//a/@href"))[1:]
    
    news_list = []

    for i in range(0, len(name_list)):
        news = {}
        new_response = requests.get(href_list[i], headers = header)
        new_dom = html.fromstring(new_response.text)
        
        date = new_dom.xpath("(//div[@class = 'wrapper'])[1]//div[@class = 'cols__inner']//span[@class = 'breadcrumbs__item']//span/@datetime")[0]
        date = parse_mail_date(date)

        resource = new_dom.xpath("(//div[@class = 'wrapper'])[1]//div[@class = 'cols__inner']//span[@class = 'breadcrumbs__item']//span/text()")[2]
        
        _id = parse_mail_id(href_list[i])
        

        news = {
            '_id' : _id,
            'name' : name_list[i],
            'href' : href_list[i],
            'resource' : resource,
            'date' : date
        }

        news_list.append(news)
    return news_list
        

def parse_mail_date(date):
    months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    month = months[int(date[6])]
    day = date[8:10]
    time = date[11:16]
    date = day + ' ' + month + ' ' + time
    return date

def parse_lenta():

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
            'Accept':'*/*'}

    link = 'https://lenta.ru/'

    response = requests.get(link, headers = header)

    dom = html.fromstring(response.text)

    main_path = "//section[@class='row b-top7-for-main js-top-seven']//div[@class='item']"
    news_blocks = dom.xpath(main_path)
    
    news_list = []
    for news_block in news_blocks:
        news = {}
        
        name = news_block.xpath(".//a//text()")[1].replace('\xa0', ' ')
        href = news_block.xpath(".//a//@href")[0].replace('\xa0', ' ')
        _id = hash(href)
        href = link.replace('/','')  + href
        resource = 'lenta.ru'
        date = news_block.xpath(".//a//@datetime")[0][9:]
        if(int(date[0:2]) < 10):
            date = '0' + date

        news = {
            '_id' : _id,
            'name' : name,
            'href' : href,
            'resource' : resource,
            'date' : date
        }

        news_list.append(news)
    
    return news_list    

def insert_into_collection(collection, data):
    for job in data:
        collection.update(job, {'upsert' : True})

def main():
    
    client = MongoClient('localhost', 27017)
    db = client['news']


    yandex = db.yandex
    yandex.drop({})
    
    mail = db.mail
    mail.drop({})

    lenta = db.lenta
    lenta.drop({})

    news = []
    news += (parse_yandex())
    yandex.insert_many(news)

    news = []
    news += (parse_mail())
    mail.insert_many(news)

    news = []
    news += (parse_lenta())
    lenta.insert_many(news)


    print(1)


if __name__ == "__main__":
    main()