# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests

class PostToServerPipeline(object):
    def process_item(self, item, spider):

        formdata = {'id':item['id'],
                    'url_source':item['url_source'],
                    'title':item['title'],
                    'location':item['location'],
                    'types':item['types'],
                    'court':item['court'],
                    'document_code':item['document_code'],
                    'document_type':item['document_type'],
                    'conclusion_date':item['conclusion_date'],
                    'proceeding':item['proceeding'],
                    'trial_person':item['trial_person'],
                    'judgment':item['judgment'],
                    'crawl_time':item['crawl_time'],
                    }
        r = requests.post(url='http://127.0.0.1:8080/api/documents',json=formdata)
        if r.status_code == 201:
            print '数据:----------%s------------提交服务器成功'%(item['id'])
        else:
            print '数据:----------%s------------提交到服务器失败'%(item['id'])
        return item
