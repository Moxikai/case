# -*- coding: utf-8 -*-
import scrapy
import re

from scrapy.selector import Selector


class ParaSpider(scrapy.Spider):
    name = "para"
    allowed_domains = ["lawxp.com"]
    start_urls = (
        'http://www.lawxp.com/Case/',
    )

    def parse(self, response):
        """一级行政区域"""
        a_list = Selector(response=response).xpath('//ul[@id="xfgdq"]/li/a')
        for a in a_list:
            pass
            link = a.xpath('@href').extract_first()
            url = 'http://www.lawxp.com/Case/'+link
            region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0)
            name = a.xpath('text()').extract_first()
            yield {'name':name,
                   'region_id':region_id,
                   'level':'1'}

