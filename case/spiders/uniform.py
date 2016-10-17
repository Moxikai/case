# -*- coding: utf-8 -*-
import re
import hashlib
import time
from scrapy.spider import CrawlSpider,Rule,Spider
from scrapy.linkextractor import LinkExtractor
from scrapy.selector import Selector
from scrapy import Request,FormRequest

from case.items import CaseItem

class UniformSpider(CrawlSpider):
    name = "uniform"
    rules = (Rule(LinkExtractor(restrict_xpaths=('//ul[@id="xfgdq"]/li/a')),
                  follow=True,
                  ),
             Rule(LinkExtractor(restrict_xpaths=('//div[@id="Group_RegionInfo1__RegionLevel2"]/ul/li/a')),
                  follow=True,
                  ),
             Rule(LinkExtractor(restrict_xpaths=('//div[@class="w-zx-nr-tj xal-bot"]/div[@class="xfg-bot1 xal-bot1"]/\
             ul/li[@class="xfg-bot13"]/a')),
                  callback='parse_list',
                  )
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

    def start_requests(self):
        """从案由类出发"""
        for topic in self.topicid_list:

            url = self.topic_url%(topic['id'])
            print '准备采集案由分类----------------%s-----------------%s' % (topic['name'],url)
            yield self.make_requests_from_url(url)

    def parse_list(self,response):
        """解析列表页"""
        # 获取当前分类下搜索结果数量
        quantity = Selector(response=response).xpath('//span[@class="xfg-yxtj4"]').re('\d{1,}')[0]
        # 解析列表项
        link_list = Selector(response=response).xpath('//div[@id="Case_List"]/ul/div[@class="gjso-list-qbt"]/\
        span[@class="fleft gjso-l-qbt"]/a/@href').extract()
        url_list = ['http://www.lawxp.com'+link for link in link_list]
        for url in url_list:
            yield Request(url=url,callback=self.parse_detail)

        # 获取下一页链接
        next_link = Selector(response=response).xpath(u'//a[contains(text(),"下一页")]/@href').extract_first()
        # 获取当前页码
        page_now = re.search(re.compile('(?<=pg=)\d{1,}'), response.url)
        if page_now:
            page_now = page_now.group(0)
        else:
            page_now = 1
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
        title = response.xpath('/html/head/title/text()').re(u'.*(?=_汇法网)')[0] # 标题,去除'_汇法网'标记
        court = response.xpath('//div[@class="zx_lin"]/a[3]/text()').extract_first()  # 法院名称
        judgment = response.xpath('//div[@id="rong_ziId"]/p').extract() # 审判书正文
        types = response.xpath('//div[@class="mylnr-jianjie"]/ul/li[2]/span[1]/a/text()').extract()
        data = response.xpath('////li[@class="mylnr-jj1"]/span/text()').extract()

        # 数据整理
        title = title.replace(' ','') # 标题去空格
        trial_person = data[-1].replace('审理人员：','').replace(' ','') # 审理人员,去除空格
        proceeding = data[-2].replace('审理程序：','') # 审理程序,去除无效数据
        conclusion_date = data[-3].replace('审结日期：','') # 审结日期
        document_type = data[-4].replace('文书类型：','') # 文书类型
        document_code = data[-5].replace('文书字号：','') # 文书字号

        # 获取区域,仅支持中级人民法院,高级人民法院
        location = re.search(re.compile(u'.*(?=中级人民法院)'),court)
        if location:
            location = location.group(0)
        else:
            location = re.search(re.compile(u'.*(?=人民法院)'),court)
            location = location.group(0)
        # 定罪类型，针对多个定罪类型
        length = len(types)
        count = length/4
        result_string = ''
        for i in range(count):
            list_split=types[i*4:(i+1)*4]
            type_string = '>>'.join(str(j) for j in list_split) # 列表转字符串
            result_string = (result_string+'\n'+type_string) if result_string else type_string

        #type_string = '>>'.join(str(i) for i in types) # 转换为str后连接
        judgment = '\n'.join(str(i) for i in judgment) # 转换为str后连接
        url = response.url
        id = self.getSignName(url)
        # 收录时间,转化为str
        crawl_time = time.time()
        crawl_time = time.localtime(crawl_time)
        crawl_time = time.strftime('%Y-%m-%d %H:%M:%S',crawl_time)

        item = CaseItem()
        item['id'] = id
        item['url_source'] = url
        item['title'] = title
        item['location'] = location
        item['types'] = result_string
        item['court'] = court
        item['document_code'] = document_code
        item['document_type'] = document_type
        item['conclusion_date'] = conclusion_date
        item['proceeding'] = proceeding
        item['trial_person'] = trial_person
        item['judgment'] = judgment
        item['crawl_time'] = str(crawl_time)
        yield item

    def getSignName(self,string):
        """获取签名"""
        sha = hashlib.sha1()
        sha.update(string)
        return sha.hexdigest()
