import scrapy, dill, os
from scrapy.crawler import CrawlerProcess
from examine.spiders.examine_spider import ExamineSpider

if __name__ == '__main__':

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(ExamineSpider)
    process.start()
    supplement_metallmind = dict()

    for supplement_name in os.listdir('supplements'):
        with open('supplements/'+supplement_name, 'rb') as f:
            supplement_info = dill.load(f)

        supplement_metallmind[supplement_name] = supplement_info

    with open('supplement metallmind', 'wb') as f:
        dill.dump(supplement_metallmind, f)
