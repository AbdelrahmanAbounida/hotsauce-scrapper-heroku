from os import stat
import time
from turtle import title
from scrapy import signals
from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import scrapy.utils.misc
import scrapy.core.scraper

from hotsauce import db
from hotsauce.Models import Product


class HotSauce(scrapy.Spider):
    name = "test"
    start_urls = ["https://hotshots.inc/", ]
    titles = []
    custom_settings = {
        'FEED_FORMAT': "csv",
        'FEED_URI': "sauces.csv"
    }
    openSpider,closeSpider = False, False

    Next = []
    links = []
    end = -1
    def warn_on_generator_with_return_value_stub(spider, callable):
        pass

    scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
    scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(HotSauce, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        self.openSpider = True
        print('======================================open===========================')
        try:
            db.session.delete(Product.query.filter_by(user_id=-2).all()[-1])
            db.session.commit()
        except:
            print("can't be deleted")
        print('======================================open===========================')

    def spider_closed(self, spider):
        self.closeSpider = True
        self.openSpider = False
        print('===================================close===========================')  
        prod = Product(title='',inStock='No',openStatus=self.openSpider,closeStatus=self.closeSpider,user_id=-2)
        db.session.add(prod)
        db.session.commit()
        print('===================================close===========================')
        

    def start_requests(self):
        filename = "sauces.csv"
        # opening the file with w+ mode truncates the file
        f = open(filename, "w+")
        f.close()
        yield scrapy.Request("https://hotshots.inc/",callback=self.parseLinks)

    def parseLinks(self, response):
        hot_sauces = response.xpath('//ul[@class="luggage_cat"]/li/a/@href').get()
        spicy_products = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-4 col-lg-4"]')[4:7]
        a = self.start_urls[0] + hot_sauces
        yield scrapy.Request(a, callback=self.filter_stocks)
        for product in spicy_products:
            categories = product.xpath(".//ul/li/a/@href").getall()
            for cat in categories:
                b = self.start_urls[0] + cat
                yield scrapy.Request(b, callback=self.filter_stocks)

    def filter_stocks(self, response):        
        b_instcok = response.xpath(
            '//a[@id="in-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()
        b_outstock = response.xpath(
            '//a[@id="out-of-stock::7::5ce79257-313a-4e04-9d95-3b5bb00a3780b8934bc5-a0f7-49ba-a588-b1c58dedff31"]/@href').get()

        try:
            instock_link = self.start_urls[0] + b_instcok
            yield scrapy.Request(instock_link, callback=self.inStockProducts)
        except:
            print()

        try:
            outstock_link = self.start_urls[0] + b_outstock
            yield scrapy.Request(outstock_link, callback=self.outStockProducts)
        except:
            print()

    def inStockProducts(self, response):
        try:
            item_scraped_count =  self.crawler.stats.get_stats()['item_scraped_count']
        except:
            item_scraped_count = 0
        try:
            p = response.xpath('//ul[@class="pagination"]')[0]
            pages = p.xpath(".//li/a/@href").getall()[1:-1]
        except:
            pages = []

        titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
        for title in titles:
            if title not in self.titles:
                self.titles.append(title)
                # product = Product(title=title,inStock="Yes")
                # db.session.add(product)
                # db.session.commit()
                yield {
                    "Title": title,
                    "Status": "Yes",
                    "close":self.closeSpider,
                    "item_scraped_count":item_scraped_count,
                }

        for page in pages:
            if 'javascript' in page:
                continue
            titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
            for title in titles:
                if title not in self.titles:
                    self.titles.append(title)
                    # product = Product(title=title,inStock="Yes")
                    # print(product)
                    # db.session.add(product)
                    # db.session.commit()
                    yield {
                        "Title": title,
                        "Status": "Yes",
                         "close":self.closeSpider,
                        "item_scraped_count":item_scraped_count,

                    }
            print('item_scraped_count',item_scraped_count)
            yield scrapy.Request(self.start_urls[0] + page, callback=self.inStockProducts)

        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and (next not in self.Next) and ('javascript' not in next):
            try:
                l = self.start_urls[0] + next
                yield scrapy.Request(l, callback=self.inStockProducts)
            except:
                print()

    def outStockProducts(self, response):
        try:
            item_scraped_count =  self.crawler.stats.get_stats()['item_scraped_count']
        except:
            item_scraped_count = 0
        try:
            p = response.xpath('//ul[@class="pagination"]')[0]
            pages = p.xpath(".//li/a/@href").getall()[1:-1]
        except:
            pages = []

        titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
        for title in titles:
            if title not in self.titles:
                self.titles.append(title)
                yield {
                    "Title": title,
                    "Status": "No",
                    "close":self.closeSpider,
                    "item_scraped_count":item_scraped_count,
                }

        for page in pages:
            if 'javascript' in page:
                continue
            titles = response.xpath('//div[@class="caption-title productname text-center"]/text()').getall()
            for title in titles:
                if title not in self.titles:
                    self.titles.append(title)
                    # product = Product(title=title,inStock="No")
                    # db.session.add(product)
                    # db.session.commit()
                    yield {
                        "Title": title,
                        "Status": "No",
                        "close":self.closeSpider,
                        "item_scraped_count":item_scraped_count,
                    }
            yield scrapy.Request(self.start_urls[0] + page, callback=self.outStockProducts)

        next = response.xpath('//a[@aria-label="Next"]/@href').get()
        if (next is not None) and (next not in self.Next) and ('javascript' not in next):
            try:
                l = self.start_urls[0] + next
                yield scrapy.Request(l, callback=self.outStockProducts)
            except:
                print()

    def Product(self, response):

        yield {
            "instock": response.meta['instock'],
            "SKU": response.xpath('//span[@id="lblSKU_659"]/text()').get(),
            "Product": response.xpath().get('//span[@class="ProductNameText"]/text()').get(),
        }


if __name__ == "__main__":
    print("Lets Gooooooo!!!")
    process = CrawlerProcess(get_project_settings())
    process.crawl(HotSauce)
    process.start()
