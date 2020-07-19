# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name =  scrapy.Field()
    target_id = scrapy.Field()
    target_name = scrapy.Field()
    photo = scrapy.Field()
