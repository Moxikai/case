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
        """检测是否登陆成功"""
        search_url = 'http://www.lawxp.com/case/?RegionId=141&q=%25e8%25af%2588%25e9%25aa%2597&WriteType=-1'
        yield Request(url=search_url,
                      callback=self.parse,
                      meta={'cookiejar':response.meta['cookiejar'],
                            'dont_cache':True},
                      dont_filter=True)


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








