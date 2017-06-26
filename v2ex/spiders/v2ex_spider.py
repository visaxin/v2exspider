#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy


class V2exSpider(scrapy.Spider):
    name = "v2ex"

    def start_requests(self):
        urls = [
            'https://www.v2ex.com/?tab=creative',
            'https://www.v2ex.com/?tab=play',
            'https://www.v2ex.com/?tab=apple',
            'https://www.v2ex.com/?tab=jobs',
            'https://www.v2ex.com/?tab=city',
            'https://www.v2ex.com/?tab=hot'
        ]

        tag = getattr(self, 'tag', None)
        if tag is not None:
            urls.append('https://www.v2ex.com/?tag=' + tag)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links = response.css("div.box span.item_title a::attr(href)").extract()

        login_url = 'https://www.v2ex.com/signin'

        form_name = scrapy.Selector(response).xpath('//input[@placeholder=$val]/@name',
                                                    val='用户名或电子邮箱地址').extract_first()
        form_password = scrapy.Selector(response).xpath('//input[@type=$val]/@name', val='password').extract_first()

        user_name = ''
        password = ''
        scrapy.FormRequest.from_response(response, formdata={
            form_name: user_name,
            form_password: password,
        })

        for l in links:
            yield scrapy.Request(response.urljoin(l),
                                 callback=self.parse_topic)

    def parse_topic(self, response):
        content = scrapy.Selector(response).css('div.topic_content *::text').extract_first()
        title = scrapy.Selector(response).xpath('//h1/text()').extract_first()
        username = scrapy.Selector(response).css('div.box div.header small.gray a::text').extract_first()
        metedata = scrapy.Selector(response).css('div.box div.header small.gray::text').extract_first()

        url = response.url

        yield {
            'title': title,
            'content': content,
            'username': username,
            'metadata': metedata,
            'url': url,
        }
