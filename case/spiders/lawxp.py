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
    server = 'http://127.0.0.1:8080/document/update'

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
            url = 'http://www.lawxp.com/case/'+link
            data = {
                    'area_first':area_name,
                    }
            # 为了获取完整区域数据，全部分解到城市
            print '一级区域-------------%s--------------搜索结果：%s个,继续按照城市分解'%(area_name,quantity)
            yield Request(url=url,
                          meta={'data':data},
                          callback=self.parseProvinceLevel)


    def parseProvinceLevel(self,response):
        """解析一级行政区域数据"""
        data = response.meta['data']
        li_list = Selector(response=response).xpath('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li')
        for li in li_list:
            link = li.xpath('a/@href').extract_first()
            url = 'http://www.lawxp.com/case/'+ link
            city_name = li.xpath('a/text()').extract_first()
            quantity = li.xpath('text()').re('\d{1,}')[0]
            data['area_second'] = city_name
            print '城市区域-----------------%s--------------搜索结果：%s个'%(city_name,quantity)
            yield Request(url=url,
                          meta={'data':data},
                          callback=self.parseCityLevel)




    def parseCityLevel(self,response):
        """解析城市级别数据"""
        data = response.meta['data']
        li_list = Selector(response=response).xpath('//div[@class="w-zx-nr-tj xal-bot"]/div/ul/li[@class="xfg-bot13"]')
        for li in li_list:
            link = li.xpath('a/@href').extract_first()
            url = 'http://www.lawxp.com/case/'+link
            quantity = li.xpath('a/@title').re('\d{1,}')[0]
            court_name = li.xpath('a/@title').re('.*(?=\d{1,})')[0]
            print '当前法院------------%s------------搜索结果-------%s个，准备开始采集'%(court_name,quantity)
            # 法院对应数据量传递过去
            data['quantity'] = quantity
            yield Request(url=url,
                          meta={'data':data},
                          callback=self.parse)


    def parse(self, response):

        link_list = response.xpath('//div[@class="gjso-list-qbt"]/span[1]/a/@href').extract()

        for link in link_list:
            url = 'http://www.lawxp.com'+link
            yield Request(url=url,
                          meta={'data':response.meta['data']},
                          callback=self.parseDetail)
        # 获取每页数据量
        count_per_page = len(link_list)
        # 计算最大页码数
        quantity = response.meta['data']['quantity']
        max_page = int(quantity)/10 + int(quantity)%10
        if max_page > 40:
            print '本次搜索结果超过40页，仍然按照总页码数40页处理'
            max_page = 40
        # 获取下一页信息
        link_next = response.xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        # 获取显示页码数
        page = re.search(re.compile('(?<=pg=)\d{1,2}'),link).group(0)
        if int(page) <= max_page and link_next:
            url_next = 'http://www.lawxp.com/case/' + link_next
            print '准备采集第-----------%s页---------------'%(page)
            yield Request(url=url_next,
                          meta={'data': response.meta['data']},
                          callback=self.parse,
                          )
        else:
            print '已达到页码上限或者完成采集'

    def parseDetail(self,response):
        """解析详细信息"""
        data = response.meta['data']
        title = response.xpath('/html/head/title/text()').extract_first()
        type_list = response.xpath('//li[@class="mylnr-jj1"][2]/span/a/text()').extract()
        types = ' '.join([str(i) for i in type_list])
        court = response.xpath('//li[@class="mylnr-jj1"][3]/span/text()').extract_first()
        document_code = response.xpath('//li[@class="mylnr-jj1"][4]/span[1]/text()').extract_first()
        document_type = response.xpath('//li[@class="mylnr-jj1"][4]/span[2]/text()').extract_first()
        conclusion_date = response.xpath('//li[@class="mylnr-jj1"][5]/span[1]/text()').extract_first()
        proceeding = response.xpath('//li[@class="mylnr-jj1"][5]/span[2]/text()').extract_first()
        judgment = response.xpath('//div[@id="rong_ziId"]').extract_first()
        """清理数据"""
        title = title.replace('_汇法网（lawxp.com）','') # 去除标题无效数据

        formdata = {
            'url':response.url,
            'title':title,
               'types':types,
               'court':court,
               'document_code':document_code,
               'document_type':document_type,
               'conclusion_date':conclusion_date,
               'proceeding':proceeding,
               'judgment':judgment,
               'area_first':data['area_first'],
               'area_second':data['area_second'],
               }
        # 替换掉None
        for key in formdata:
            if formdata[key] is None:
                formdata[key] = ''
        yield Request(url=self.server,
                      meta={'formdata': formdata,
                            'dont_cache': True},
                      callback=self.postToServer,
                      dont_filter=True,
                      )

    def postToServer(self, response):
        """提交数据到服务器"""
        # print response.body
        csrf_token = response.xpath('//input[@id="csrf_token"]/@value').extract_first()
        print 'csrf_token:', csrf_token
        formdata = response.meta['formdata']
        formdata['csrf_token'] = csrf_token
        yield FormRequest.from_response(response, formdata=formdata)







