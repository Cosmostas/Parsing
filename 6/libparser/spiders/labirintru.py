import scrapy
from scrapy.http import HtmlResponse
from libparser.items import LibparserItem

class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?stype=0']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.pagination-next__text::attr(href)').extract_first()

        book_links = response.css('a.product-title-link::attr(href)').extract()
         
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)
    


    def book_parse(self, response:HtmlResponse):
        name_book = response.css('h1::text').extract_first()
        href_book = response.url
        autor_book =  response.css('a[data-event-label=author]::text').extract_first()
        main_price_book = response.css('span[class=buying-priceold-val-number]::text').extract_first()

        if main_price_book == None:
            main_price_book = response.css('span.buying-price-val-number::text').extract_first()
            actual_price_book = main_price_book
        else:
            actual_price_book = response.css('span[class=buying-pricenew-val-number]::text').extract_first()
        rate_book = response.css('div[id=rate]::text').extract_first()
        yield LibparserItem(name=name_book,
                            href=href_book,
                            autor=autor_book,
                            main_price=main_price_book,
                            actual_price=actual_price_book,
                            rate=rate_book)