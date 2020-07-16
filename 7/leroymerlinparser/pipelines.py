# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline


import scrapy
from pymongo import MongoClient

class DataBasePipeline:
    def __init__(self):
        self.client = MongoClient('localhost',27017)
        self.mongo_base = self.client.leroymerlin
        self.mongo_base['leroymerlinru'].drop()
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
    def __del__(self):
        self.client.close()




class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img,meta=item)
                except Exception as e:
                    print(e)

    def parse_specifications(self, item):
        item["specifications"] = []
        specifications_category = item['specifications_category']
        specifications_value = item['specifications_value']
        for i in range(len(specifications_category)):
            item["specifications"].append( {'specifications_category' : specifications_category[i], 'specifications_value' : specifications_value[i]} )

        item.pop('specifications_category', None)
        item.pop('specifications_value', None)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
            item['price'] = item['price'][0] 
            item['_id'] = self.parse_id(item['url'])
            self.parse_specifications(item)
        return item

    def parse_id(self, url):
        end_pos = len(url) - 1
        beg_pos = 0
        for i in range(end_pos, 0, -1):
            if url[i] == '-':
                beg_pos = i + 1
                break
        _id = url[beg_pos:end_pos]
        return _id
    
    def file_path(self, request, response=None, info=None):
        item = request.meta
        return f'full/{item["name"]}/{item["photos"].index(request.url)}.jpg'
