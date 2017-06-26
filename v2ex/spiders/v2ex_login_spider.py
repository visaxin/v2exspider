#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy
from elasticsearch import Elasticsearch


class V2exSpider(scrapy.Spider):
    name = "v2exlogin"
    urls = [
        'https://www.v2ex.com/?tab=deals',
        'https://www.v2ex.com/?tab=creative',
        'https://www.v2ex.com/?tab=play',
        'https://www.v2ex.com/?tab=apple',
        'https://www.v2ex.com/?tab=jobs',
        'https://www.v2ex.com/?tab=city',
        'https://www.v2ex.com/?tab=hot'
    ]

    es_client = Elasticsearch()

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        'Origin': 'http://www.v2ex.com',
    }

    def start_requests(self):
        login_url = ['https://www.v2ex.com/signin']
        yield scrapy.Request(url=login_url[0], callback=self.login)

    def login(self, response):
        form_name = scrapy.Selector(response).xpath('//input[@placeholder=$val]/@name',
                                                    val='用户名或电子邮箱地址').extract_first()
        form_password = scrapy.Selector(response).xpath('//input[@type=$val]/@name', val='password').extract_first()

        print form_name
        print form_password

        once = scrapy.Selector(response).xpath('//input[@name=$val]/@value', val='once').extract_first()
        user_name = ''
        password = ''
        print once

        return scrapy.FormRequest.from_response(response,
                                                formxpath='//form[@action="/signin"]',
                                                # headers=response.headers,
                                                formdata={
                                                    form_name: user_name,
                                                    form_password: password,
                                                    'once': once,
                                                    'next': "/",
                                                }, callback=self.after_login,
                                                dont_filter=True,
                                                )

    def after_login(self, response):
        with open("body.html", 'wb+') as f:
            f.write(response.body)
        print response.url
        print response.status
        for i, url in enumerate(self.urls):
            yield scrapy.Request(url=url, callback=self.parse, headers=response.headers,
                                 meta={'tag': url.split('=')[1]})

    def parse(self, response):
        print response
        links = response.css("div.box span.item_title a::attr(href)").extract()
        for l in links:
            yield scrapy.Request(response.urljoin(l),
                                 callback=self.parse_topic)

    def parse_topic(self, response):
        content = scrapy.Selector(response).css('div.topic_content *::text').extract_first()
        title = scrapy.Selector(response).xpath('//h1/text()').extract_first()
        username = scrapy.Selector(response).css('div.box div.header small.gray a::text').extract_first()
        metedata = scrapy.Selector(response).css('div.box div.header small.gray::text').extract_first()

        url = response.url

        yield self.es_client.index(index='v2ex',
                                   doc_type='app',
                                   body={
                                       'title': title,
                                       'content': content,
                                       'username': username,
                                       'metadata': metedata,
                                       'url': url,
                                       'tag': response.meta['tag'],
                                   })
