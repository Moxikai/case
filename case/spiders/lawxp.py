# -*- coding: utf-8 -*-

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy

from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose,Join

from case.items import CaseItem
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
        """

        l = ItemLoader(item=CaseItem(),response=response)
        l.add_xpath('title','/html/head/title/text()',TakeFirst,unicode.title) # 标题
        l.add_xpath('types','//li[@class="mylnr-jj1"][2]/span/a/text()',unicode.title,Join) # 类型，还需转字符串
        l.add_xpath('court','//li[@class="mylnr-jj1"][3]/span/text()',TakeFirst) # 审理法院
        l.add_xpath('document_code', '//li[@class="mylnr-jj1"][4]/span[1]/text()', TakeFirst) # 文书字号
        l.add_xpath('document_type', '//li[@class="mylnr-jj1"][4]/span[2]/text()', TakeFirst) # 文书类型
        l.add_xpath('conclusion_date','//li[@class="mylnr-jj1"][5]/span[1]/text()',TakeFirst) # 审结日期
        l.add_xpath('proceeding','//li[@class="mylnr-jj1"][5]/span[2]/text()',TakeFirst) # 审理程序
        l.add_xpath('judgment','//div[@id="rong_ziId"]',TakeFirst,unicode.title) # 判决书
        l.load_item()
        """
        title = response.xpath('/html/head/title/text()').extract_first()
        type_list = response.xpath('//li[@class="mylnr-jj1"][2]/span/a/text()').extract()
        types = ' '.join([str(i) for i in type_list])
        court = response.xpath('//li[@class="mylnr-jj1"][3]/span/text()').extract_first()
        document_code = response.xpath('//li[@class="mylnr-jj1"][4]/span[1]/text()').extract_first()
        document_type = response.xpath('//li[@class="mylnr-jj1"][4]/span[2]/text()').extract_first()
        conclusion_date = response.xpath('//li[@class="mylnr-jj1"][5]/span[1]/text()').extract_first()
        proceeding = response.xpath('//li[@class="mylnr-jj1"][5]/span[2]/text()').extract_first()
        judgment = response.xpath('//div[@id="rong_ziId"]').extract_first()
        yield {'title':title,
               'types':types,
               'court':court,
               'document_code':document_code,
               'document_type':document_type,
               'conclusion_date':conclusion_date,
               'proceeding':proceeding,
               'judgment':judgment,
               }








