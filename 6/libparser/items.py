# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LibparserItem(scrapy.Item):
    # define the fields for your item here like:]
    _id = scrapy.Field()
    name = scrapy.Field()
    href = scrapy.Field()
    autor = scrapy.Field()
    main_price = scrapy.Field()
    actual_price = scrapy.Field()
    rate = scrapy.Field()
