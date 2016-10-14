# -*- coding: utf-8 -*-
import scrapy

from scrapy.spider import CrawlSpider,Rule,Spider
from scrapy.linkextractor import LinkExtractor
from scrapy.selector import Selector
from scrapy import Request



class UniformSpider(Spider):
    name = "uniform"

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
            print '准备采集案由分类----------------%s-----------------'%(topic['name'])
            yield Request(url=self.topic_url%(topic['id']),callback=self.parse)

    def parse(self,response):
        """"""

