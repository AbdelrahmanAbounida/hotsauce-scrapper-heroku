from operator import le
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scrapy.signalmanager import dispatcher


from run import HotSauce


def spider_results():
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process = CrawlerProcess(get_project_settings())
    process.crawl(HotSauce)
    process.start()  # the script will block here until the crawling is finished
    yield results


if __name__ == '__main__':
    for i in spider_results():
        print('===========================================')
        print(i['Status'])
        print('===========================================')
