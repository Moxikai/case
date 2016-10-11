# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy

from scrapy import Request

class LawxpSpider(scrapy.Spider):
    name = "lawxp"
    allowed_domains = ["lawxp.com"]
    start_urls = (
        'http://www.lawxp.com/case',
    )

    def parse(self, response):

        link_list = response.xpath('//div[@class="gjso-list-qbt"]/span[1]/a/@href').extract()
        #code_publish = response.xpath('//span[@class="zyin-ll-bt2"]')
        for link in link_list:
            url = 'http://www.lawxp.com/'+link
            yield Request(url=url,callback=self.parseDetail)
        # 获取下一页信息
        link_next = response.xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        if link_next:
            url_next = 'http://www.lawxp.com/'+link_next
            
            yield Request(url=url_next,callback=self.parse)
        else:
            print '获取下一页失败！'

    def parseDetail(self,response):
        """解析详细信息"""


        title = response.xpath('/html/head/title/text()').extract_first()
        print '案例：---------------------%s-----------------------页面下载成功'%(title),'\n'
        #print response.body
        yield {'title':title,
               'url':response.url}


