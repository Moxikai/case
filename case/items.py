# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field,Item

class CaseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    title = Field() # 标题
    types = Field() # 案件类型，从主要到细分，多个值
    court = Field() # 审理法院
    document_code = Field() # 文书字号
    document_type = Field() # 文书类型
    conclusion_date = Field() # 审结日期
    proceeding = Field() # 审理程序，一审、二审等等
    trial_persons = Field() # 审理人员
    judgment = Field() # 判决书
    crawl_date = Field() # 爬虫收录日期

