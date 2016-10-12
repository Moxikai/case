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
    username = ''
    password = ''


    def start_requests(self):
        """启动登陆"""
        yield Request(url=self.login_url,
                      callback=self.login,
                      meta={'cookiejar':1,
                            'dont_cache':True},
                      dont_filter=True)

    def login(self,response):
        """登陆"""
        __EVENTTARGET = response.xpath('//input[@id="__EVENTTARGET"]/@value').extract_first()
        __EVENTARGUMENT = response.xpath('//input[@id="__EVENTARGUMENT"]/@value').extract_first()
        __VIEWSTATE = response.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        __VIEWSTATEGENERATOR = response.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first()
        __EVENTVALIDATION = response.xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()
        lbl_returnUrl = response.xpath('//input[@id="lbl_returnUrl"]/@value').extract_first()
        ipturl = response.xpath('//input[@id="ipturl"]/@value').extract_first()
        #nameredio = response.xpath('//input[@id="nameredio"]/@value').extract_first()

        formdata = {
            '__EVENTTARGET':__EVENTTARGET,
            '__EVENTARGUMENT':__EVENTARGUMENT,
            '__VIEWSTATE':__VIEWSTATE,
            '__VIEWSTATEGENERATOR':__VIEWSTATEGENERATOR,
            '__EVENTVALIDATION':__EVENTVALIDATION,
            'lbl_returnUrl':lbl_returnUrl,
            'ipturl':ipturl,
            'nameredio':'0',
            'username':self.username,
            'password':self.password,
            'btnLogin':'登陆',
            'mobilePhone':'',
            'dyPwdFirst':'',
            'coks1':'on'
        }
        print formdata
        yield FormRequest.from_response(response,
                                        formdata=formdata,
                                        callback=self.afterlogin,
                                        meta={'cookiejar':response.meta['cookiejar'],
                                              'dont_cache':True})

    def afterlogin(self,response):
        """请求关键字：诈骗，全文搜索"""
        search_url = 'http://www.lawxp.com/case/?q=%E8%AF%88%E9%AA%97&t=2'
        yield Request(url=search_url,
                      callback=self.parse,
                      meta={'cookiejar':response.meta['cookiejar'],
                            'dont_cache':True},
                      dont_filter=True)

    def parseFirstLevel(self,response):
        """第一级判断：总数据是否超过400;
        如果超过400,则获取一级地区链接
        """
        result_count = Selector(response=response).xpath('//span[@class="xfg-yxtj4"]/text()').re('\d{1,}')
        if result_count:
            count = result_count[0]
            print '当前搜索条件共有记录：----------------%s个-------------------'%count
            if int(count) > 400:
                # 获取一级地区链接，记录数量
                a_list = Selector(response=response).xpath('//ul[@id="xfgdq"]/li/a')
                for a in a_list:
                    if a:
                        link = a.xpath('@href').extract_first()
                        area_name = a.xpath('text()').extract_first()
                        quantity = a.xpath('@title').re('\d{1,}')[0]
                        region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0)
                        url = 'http://www.lawxp.com/case/'+link
                        data = {
                            'region_id':region_id,
                            'area_name':area_name,
                            'url':url,
                            'quantity':int(quantity)
                        }
                        yield Request(url=data['url'],
                                      meta={
                                          'data':data,
                                          'cookiejar':response.meta['cookiejar']},
                                      callback=self.parseSecondLevel
                                      )
            else:
                print '当前搜索结果小于400,准备直接开始采集！'
                yield self.parse(response)


    def parseSecondLevel(self,response):
        """解析一级地区"""
        data = response.meta['data']
        if data['quantity'] > 400:
            pass
            # 获取二级地区链接
            li_list = Selector(response=response).xpath('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li')
            for li in li_list:
                if li:
                    link = li.xpath('a/@href').extract_first()
                    url = 'http://www.lawxp.com/case/'+link
                    second_area_name = li.xpath('a/text()').extract_first()
                    quantity = li.xpath('text()').re('\d{1,}')[0]
                    # 二级地区id
                    region_id = re.search(re.compile('(?<=RegionId=)\d{1,}'),link).group(0)
                    second_data = {'region_id':region_id,
                                   'second_area_name':second_area_name,
                                   'url':url,
                                   'quantity':int(quantity),
                                   }
                    # 转到二级地区链接
                    yield Request(url=second_data['url'],
                                  callback=self.parseThirdLevel,
                                  meta={'cookiejar':response.meta['cookiejar'],
                                        'second_data':second_data})
        else:
            yield self.parse(response)


    def parseThirdLevel(self,response):
        """解析二级地区"""
        second_data = response.meta['second_data']
        if second_data['quantity'] > 400:
            # 二级区域结果数量大于400,则分法院链接再分解
            li_list = Selector(response=response).xpath('//li[@class="xfg-bot13"]')
            for li in li_list:
                if li:
                    link = li.xpath('a/@href').extract_first()
                    #court_id = re.search(re.compile('(?<=CourtId=)\d{1,}'),link).group(0)
                    quantity = li.xpath('a/@title').re('\d{1,}')[0]
                    #court_name = li.xpath('a/@title').re('.*(?=\d{1,})')[0]
                    url = 'http://www.lawxp.com/case/' + link
                    third_data = {'url':url,
                                  'quantity':int(quantity)}
                    # 暂时不考虑 按照案件类型细分
                    
                    yield Request(url=third_data['url'],
                                  callback=self.parse,
                                  meta={'cookiejar':response.meta['cookiejar'],
                                        'third_data':third_data})

        else:
            # 二级区域结果数量不大于400，直接开始采集
            yield self.parse(response)



    def parse(self, response):

        link_list = response.xpath('//div[@class="gjso-list-qbt"]/span[1]/a/@href').extract()

        for link in link_list:
            url = 'http://www.lawxp.com'+link
            yield Request(url=url,callback=self.parseDetail,meta={'cookiejar':response.meta['cookiejar']})
        # 获取下一页信息
        link_next = response.xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        if link_next:
            url_next = 'http://www.lawxp.com/case/'+link_next
            print '准备采集下一页：----------------%s--------------------'%(url_next)
            yield Request(url=url_next,
                          callback=self.parse,
                          meta={'cookiejar':response.meta['cookiejar']}
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








