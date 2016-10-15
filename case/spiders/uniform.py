# -*- coding: utf-8 -*-
import re
import hashlib

from scrapy.spider import CrawlSpider,Rule,Spider
from scrapy.linkextractor import LinkExtractor
from scrapy.selector import Selector
from scrapy import Request,FormRequest


class UniformSpider(CrawlSpider):
    name = "uniform"
    rules = (Rule(LinkExtractor(restrict_xpaths=('//ul[@id="xfgdq"]/li/a/@href')),
                  follow=True,
                  process_links='join_url'),
             Rule(LinkExtractor(restrict_xpaths=('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li/a/@href')),
                  follow=True,
                  process_links='join_url'),
             Rule(LinkExtractor(restrict_xpaths=('//div[@class="w-zx-nr-tj xal-bot"]/div[@class="xfg-bot1 xal-bot1"]/\
             ul/li[@class="xfg-bot13"]/a/@href')),
                  callback='parse_list',
                  process_links='join_url')
             )
    topicid_list =[{'id':'20150',
                    'name':'非法吸收公众存款罪'},
                   {'id':'20151',
                    'name':'伪造、变造金融票证罪'},
                   {'id':'20152',
                    'name':'伪造、变造国家有价证券罪'},
                   {'id':'20153',
                    'name':'伪造、变造股票、公司、企业'},
                   {'id':'20156',
                    'name':'编造并传播证券、期货交易虚假信息罪'},
                   {'id':'20157',
                    'name':'诱骗投资者买卖证券、期货合约罪'},
                   {'id':'20161',
                    'name':'吸收客户资金不入账罪'},
                   {'id':'20635',
                    'name':'骗取贷款、票据承兑、金融票证罪'},
                   {'id':'20637',
                    'name':'窃取、收买、非法提供信用卡信息罪'},
                   {'id':'20167',
                    'name':'集资诈骗罪'},
                   {'id':'20168',
                    'name':'贷款诈骗罪'},
                   {'id':'20169',
                    'name':'票据诈骗罪'},
                   {'id':'20170',
                    'name':'金融凭证诈骗罪'},
                   {'id':'20171',
                    'name':'信用证诈骗罪'},
                   {'id':'20172',
                    'name':'信用卡诈骗罪'},
                   {'id':'20173',
                    'name':'有价证券诈骗罪'},
                   {'id':'20174',
                    'name':'保险诈骗罪'},
                   {'id':'20201',
                    'name':'合同诈骗罪'},
                   {'id':'20204',
                    'name':'伪造倒卖伪造的有价票证罪'},
                   {'id':'20207',
                    'name':'提供虚假证明文件罪'},
                   {'id':'20642',
                    'name':'组织、领导传销活动罪'},
                   ]
    topic_url = 'http://www.lawxp.com/case/?TopicId=%s&WriteType=-1'

    def join_url(self,links):
        """处理提取的链接"""
        base_url = 'http://www.lawxp.com/case/'
        return [base_url+link for link in links]

    def start_requests(self):
        """从案由类出发"""
        for topic in self.topicid_list:
            print '准备采集案由分类----------------%s-----------------'%(topic['name'])
            yield self.make_request_from_url(topic%(topic['id']))

    def parse_list(self,response):
        """解析列表页"""
        # 获取当前分类下搜索结果数量
        quantity = Selector(response=response).xpath('//span[@class="xfg-yxtj4"]').re('\d{1,}')[0]
        """
        if int(quantity) < 1:
            print '当前分类下搜索结果为0或者解析列表页出现错误,请检查--------%s---------'%(response.url)
        # 计算最大页码
        max_page = int(quantity)/10+int(quantity)%10
        if max_page > 40:
            max_page = 40 # 最大能够处理的页面为40页
            print '当前分类下搜索结果超过40页,默认按照40页处理,请检查---------%s--------'%(response.url)
        """
        # 解析列表项
        link_list = Selector(response=response).xpath('//div[@id="Case_List"]/ul/div[@class="gjso-list-qbt"]/\
        span[@class="fleft gjso-l-qbt"]/a/@href').extract()
        url_list = ['http://www.lawxp.com'+link for link in link_list]
        for url in url_list:
            yield Request(url=url,callback=self.parse_detail)

        # 获取下一页链接
        next_link = Selector(response=response).xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        # 获取当前页码
        page_now = re.search(re.compile('(?<=pg=)\d'), response.url).group(0)
        if next_link:
            next_url = 'http://www.lawxp.com/case/'+next_link
            if int(page_now) == 40:
                print '当前分类下已达到最大处理页码40,请检查--------------%s-------------'%(response.url)
            else:
                yield Request(url=next_url,callback=self.parse_list)
        else:
            print '当前分类搜索结果数:------%s个--------当前页码:-------%s--------请检查url:\
            ---------%s---------'%(quantity,page_now,response.url)

    def parse_detail(self,response):
        """解析详细页面"""
        title = Selector(response=response).xpath('/html/head/title/text()').re(u'.*(?=_汇法网)')[0] # 标题,去除'_汇法网'标记
        ul = Selector(response=response).xpath('//div[@class="mylnr-jianjie"]/ul')
        types = ul.xpath('li[2]/span/a/text()').extract() # 案由
        court = Selector(response=response).xpath('//div[@id="court_history"]/div/span/strong/text()').extract_first() # 法院名称
        document_code = ul.xpath('li[4]/span[1]/text()').re(u'(?<=文书字号：).*')[0] # 文书字号
        document_type = ul.xpath('li[4]/span[2]/text()').re(u'(?<=文书类型：).*')[0] # 文书类型
        conclusion_date = ul.xpath('li[5]/span[1]/text()').re('\d{4}-\d{2}-\d{2}')[0] # 审结日期
        proceeding = ul.xpath('li[5]/span[2]/text()').re(u'(?<=审理程序：).*')[0] # 审理程序
        trial_person = ul.xpath('li[6]/span/text()').re(u'(?<=审理人员：).*')[0] # 审理人员
        judgment = Selector(response=response).xpath('//div[@id="rong_ziId"]/p').extract() # 审判书正文

        #数据整理
        type_string = '>>'.join(str(i) for i in types) # 转换为str后连接
        judgment = '\n'.join(str(i) for i in judgment) # 转换为str后连接
        url = response.url
        id = self.getSignName(url)
        formdata = {'id':id,
                    'url':url,
                    'title':title,
                    'types':type_string,
                    'court':court,
                    'document_code':document_code,
                    'document_type':document_type,
                    'conclusion_date':conclusion_date,
                    'proceeding':proceeding,
                    'trial_person':trial_person,
                    'judgment':judgment,
                    }
        yield Request(url='http://127.0.0.1:8080/document/update',
                      callback=self.post_to_server,
                      dont_filter=True,
                      meta={'dont_cache':True,
                            'formdata':formdata})

    def post_to_server(self,response):
        """post方式上传到服务器"""
        csrf_token = Selector(response=response).xpath('//input[@id="csrf_token"]/@value').extract_first()
        formdata = response.meta['formdata']
        formdata['csrf_token'] = csrf_token
        formdata['submit'] = 'submit'
        # 处理None
        for key in formdata:
            if formdata[key] is None:
                formdata[key] = ''
        yield FormRequest.from_response(response=response,
                                        formdata=formdata,
                                        meta={'dont_cache':True,
                                              'formdata':formdata},
                                        callback=self.after_post)



    def after_post(self,response):
        """返回item,切断response回路"""
        yield response.meta['formdata']


    def getSignName(self,string):
        """获取签名"""
        sha = hashlib.sha1()
        sha.update(string)
        return sha.hexdigest()





