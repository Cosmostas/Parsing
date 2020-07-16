import scrapy
from scrapy.http import HtmlResponse
from leroymerlinparser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    main_url = 'https://leroymerlin.ru'

    def __init__(self, search):
        self.start_urls = [f'{self.main_url}/search/?q={search}']

    def parse(self, response):
        next_page = response.css('a.next-paginator-button::attr(href)').extract_first()
        
        product_links = response.css('a.product-name-inner::attr(href)').extract()
        for link in product_links:
           yield response.follow(f'{self.main_url}{link}',callback=self.parse_product)
         
        yield response.follow(f'{self.main_url}{next_page}', callback=self.parse)

    def parse_product(self, response:HtmlResponse):


        loader = ItemLoader(item=LeroymerlinparserItem(),response=response)
        loader.add_css('name','h1[slot=title]::text')
        loader.add_xpath('photos',"//img[@slot = 'thumbs']/@src")
        loader.add_value('url', response.url)
        loader.add_css('price','span[slot=price]::text')
        loader.add_css('specifications_category','div.def-list__group dt::text')
        loader.add_css('specifications_value','div.def-list__group dd::text')
        yield loader.load_item()