from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlinparser.spiders.leroymerlinru import LeroymerlinruSpider
from leroymerlinparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider,search='Фанера')

    process.start()