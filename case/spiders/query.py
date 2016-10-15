# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.selector import Selector
from scrapy import Request

class QuerySpider(scrapy.Spider):
    name = "query"
    #allowed_domains = ["lawxp.com"]
    start_urls = (
        'http://www.lawxp.com/case',
    )

    def parse(self, response):
        """解析一级行政单位"""
        a_list = Selector(response=response).xpath('//ul[@id="xfqdq"]/li/a') # 排除无效数据
        for a in a_list:
            name = a.xpath('text()').extract_first() # 一级行政单位
            link = a.xpath('@href').extract_first()
            region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0) # 一级行政单位id
            url = 'http://www.lawxp.com/case/'+link
            data = {'region_id':region_id,
                                'name':name,}
            yield Request(url=url,
                          meta={'data':data},
                          callback=self.parseFirstCourt,
                          )
    def parseFirstCourt(self,response):
        """解析一级行政单位对应法院"""
        data = response.meta['data']
        ul = Selector(response=response).xpath('//div[@class="w-zx-nr-tj xal-bot"][1]/div/ul')
        # 解析一级对应法院
        a = ul.xpath('/li[class="xfg-bot12"][1]/a')
        court_id = a.xpath('@href').re('(?<=CourtId=)\d{1,}')[0]
        data['court_id'] = court_id
        yield data
        li_list = Selector(response=response).xpath('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li')
        for li in li_list:
            second_name = li.xpath('a/text()').extract_first() # 二级行政单位
            link = li.xpath('a/@href').extract_first()
            second_region_id = re.search(re.compile('(?<=RegionId=)'),link).group(0) # 二级行政单位id
            data['second_name'] = second_name
            data['second_region_id'] = second_region_id
            url = 'http://www.lawxp.com/case/'+link
            yield Request(url=url,
                          meta={'data':data},
                          callback=self.parseCourt,
                          )

    def parseCourt(self,response):
        """解析法院列表"""






