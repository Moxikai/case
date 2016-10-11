# -*- coding: utf-8 -*-

import re
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
            url = 'http://www.lawxp.com'+link
            yield Request(url=url,callback=self.parseDetail)
        # 获取下一页信息
        link_next = response.xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        if link_next:
            url_next = 'http://www.lawxp.com/Case/'+link_next
            # 判断是否循环链接
            if url_next == response.url:
                print '遇到循环链接,准备页码手动自增1'
                pg = re.search(re.compile('(?<=pg=)\d{1,}'),url_next).group(0)
                url_next = 'http://www.lawxp.com/Case/?pg=%s&WriteType=-1'%(int(pg)+1)
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


