from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.followers import InstagramSpider as FollowersSpider
from instaparser.spiders.following import InstagramSpider as FollowingSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(FollowersSpider)
    process.crawl(FollowingSpider)
    process.start()