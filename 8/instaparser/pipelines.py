# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline

class InstaparserPipeline:
    def __init__(self):
        self.client = MongoClient('localhost',27017)
        self.mongo_base = self.client.Insta
        self.mongo_base['followers'].drop()
        self.mongo_base['following'].drop()
    def process_item(self, item, spider):
        item["_id"] = item["user_id"] + "_" + item["target_id"] 
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
    def __del__(self):
        self.client.close()
