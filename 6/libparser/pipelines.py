# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class LibparserPipeline:
    def __init__(self):
        self.client = MongoClient('localhost',27017)
        self.mongo_base = self.client.book

    def process_item(self, item, spider):
        if spider.name == 'labirintru':
            _id = self.process_id_labirint(item['href'])
            #_id = hash(item['href'])
        elif spider.name == 'book24ru':
            _id = self.process_id_book24(item['href'])

        item['_id'] = _id
        
        item['main_price'] = int(item['main_price'])
        item['actual_price'] = int(item['actual_price'])
        item['rate'] = float(item['rate'])

        collection = self.mongo_base[spider.name]
        collection.replace_one(item, item, upsert=True)

        return item
    

    def process_id_labirint(self, href):
        beg_pos = href.find('books/') + 6
        _id = href[beg_pos:-1]
        return _id
    def process_id_book24(self, href):
        end_pos = len(href) - 1
        for i in range(end_pos, 0, -1):
            if href[i] == '-':
                beg_pos = i + 1
                break
        
        _id = href[beg_pos:end_pos]
        return _id

    def __del__(self):
            self.client.close()
