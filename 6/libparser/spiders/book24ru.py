import scrapy
from scrapy.http import HtmlResponse
from libparser.items import LibparserItem
import numpy as np

class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/?q=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a._text::attr(href)').extract_first()

        book_links = response.css('a.book__title-link::attr(href)').extract()
         
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        yield response.follow(next_page, callback=self.parse)
    


    def book_parse(self, response:HtmlResponse):
        name_book = response.css('h1::text').extract_first()
        href_book = response.url
        autor_book = response.css('a.js-data-link::text').extract_first()
        if autor_book == None:
            autor_book = response.css('a.item-tab__chars-link::text').extract()[2].replace('  ','').replace('\n','')
        
        main_price_book = response.css('div.item-actions__price-old::text').extract_first()
        actual_price_book = response.css('div.item-actions__price b::text').extract_first()
        if main_price_book == None:
            main_price_book = actual_price_book
        main_price_book = main_price_book.replace(' р.', '')
        rate_book = response.css('span.rating__rate-value::text').extract_first()
        if rate_book == None:
            rate_book = np.nan
        else:
            rate_book = rate_book.replace(',', '.')
        yield LibparserItem(name=name_book,
                            href=href_book,
                            autor=autor_book,
                            main_price=main_price_book,
                            actual_price=actual_price_book,
                            rate=rate_book)