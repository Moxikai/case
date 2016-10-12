# -*- coding: utf-8 -*-

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
import urlparse
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose,Join
from scrapy import FormRequest
from scrapy.selector import Selector

from case.items import CaseItem
class LawxpSpider(scrapy.Spider):
    name = "lawxp"
    #allowed_domains = ["lawxp.com"]
    login_url = 'http://www.lawxp.com/wl/Login.aspx'
    case_url = 'http://www.lawxp.com/Case/'
    sear_url = ''

    def start_requests(self):
        """请求入口"""
        url = 'http://www.lawxp.com/Case/?TopicId=20166&WriteType=-1#list' # 金融诈骗
        yield Request(url=url,
                      callback=self.getProvinceList,
                      meta={'dont_cache':True}
                      ) # 按照省级行政区分级

    def getProvinceList(self,response):
        """获取行政区划列表及搜索结果数量"""
        total_count = Selector(response=response).xpath('//span[@class="xfg-yxtj4"]/text()').re('\d{1,}')[0]
        print '当前搜索结果---------------%s个-----------------'%(total_count)

        a_list = Selector(response=response).xpath('//ul[@id="xfgdq"]/li/a')
        for a in a_list:
            link = a.xpath('@href').extract_first()
            quantity = a.xpath('@title').re('\d{1,}')[0]
            area_name = a.xpath('text()').extract_first()
            region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0)
            url = 'http://www.lawxp.com/case/'+link
            data = {'region_id':region_id,
                    'area_name':area_name,
                    'url':url,
                    'quantity':int(quantity),
                    }

            if data['quantity'] > 400:
                print '一级区域-------------%s--------------搜索结果大于400,继续按照城市分解'%(area_name)
                yield Request(url=data['url'],
                              callback=self.parseProvinceLevel)
            else:
                print '一级区域-------------%s---------------搜索结果不大于400,准备直接采集'%(area_name)
                yield Request(url=data['url'],
                              callback=self.parse)

    def parseProvinceLevel(self,response):
        """解析一级行政区域数据"""
        li_list = Selector(response=response).xpath('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li')
        for li in li_list:
            link = li.xpath('a/@href').extract_first()
            url = 'http://www.lawxp.com/case/'+ link
            city_name = li.xpath('a/text()').extract_first()
            region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0)
            quantity = li.xpath('text()').re('\d{1,}')[0]
            data = {'region_id':region_id,
                    'area_name':city_name,
                    'url':url,
                    'quantity':int(quantity),
                    }
            if data['quantity'] > 400:
                print '城市区域-----------------%s---------------搜索结果大于400,继续按照法院分解'%(data['area_name'])
                yield Request(url=url,
                              callback=self.parseCityLevel)
            else:
                print '城市区域------------------%s----------------搜索结果不大于400,准备直接采集'%(data['area_name'])
                yield Request(url=url,callback=self.parse)



    def parseCityLevel(self,response):
        """解析城市级别数据"""

        li_list = Selector(response=response).xpath('//li[@class="xfg-bot13"]')
        for li in li_list:
            link = li.xpath('a/@href').extract_first()
            url = 'http://www.lawxp.com/case/'+link
            quantity = li.xpath('a/@title').re('\d{1,}')[0]
            court_name = li.xpath('a/@title').re('.*(?=\d{1,})')[0]
            print '当前法院------------%s------------搜索结果-------%s个，准备开始采集'%(court_name,quantity)
            yield Request(url=url,callback=self.parse)






    def parse(self, response):

        link_list = response.xpath('//div[@class="gjso-list-qbt"]/span[1]/a/@href').extract()

        for link in link_list:
            url = 'http://www.lawxp.com'+link
            yield Request(url=url,callback=self.parseDetail)
        # 获取下一页信息
        link_next = response.xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        if link_next:
            url_next = 'http://www.lawxp.com/case/'+link_next
            print '准备采集下一页：----------------%s--------------------'%(url_next)
            yield Request(url=url_next,
                          callback=self.parse,
                          )
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
        yield {'url':response.url,
            'title':title,
               'types':types,
               'court':court,
               'document_code':document_code,
               'document_type':document_type,
               'conclusion_date':conclusion_date,
               'proceeding':proceeding,
               'judgment':judgment,
               }








