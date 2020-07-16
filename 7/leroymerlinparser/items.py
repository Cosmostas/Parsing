# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def cleaner_photo(value):
    return value.replace('w_82,h_82', 'w_1200,h_1200')

def cleaner_price(value):
    return int(value.replace(' ',''))

def cleaner_specifications(value):
    return value.replace('  ', '').replace('\n', '')

class LeroymerlinparserItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(cleaner_price))
    specifications = scrapy.Field()
    specifications_category = scrapy.Field(input_processor=MapCompose(cleaner_specifications))
    specifications_value = scrapy.Field(input_processor=MapCompose(cleaner_specifications))