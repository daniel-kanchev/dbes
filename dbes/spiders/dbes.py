import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from dbes.items import Article


class DbesSpider(scrapy.Spider):
    name = 'dbes'
    start_urls = ['https://www.db.com/spain/es/content/Notas-de-prensa.html']

    def parse(self, response):
        years = response.xpath('//div[@id="leftNavi"]//li/a/@href').getall()
        yield from response.follow_all(years, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//td/a[@class="font5 block"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()
        #
        date = response.xpath('//div[@id="cc_02a_NewsArticle"]/text()').get() or \
               response.xpath('//div[@class="font3 onebreak top12"]/text()[2]').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@id="cc_02a_NewsArticle"]//text()').getall() or \
                  response.xpath('//div[@id="col2"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
