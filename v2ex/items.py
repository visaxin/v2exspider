# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class V2ExItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    user_name = scrapy.Field()
    meta_data = scrapy.Field()

    def process_item(self, item, spider):
        pass

class LoginItem(scrapy.Item):
    image_url = scrapy.Field()
