# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import json

reload(sys) 
sys.setdefaultencoding('utf-8')

class NjuptPipeline(object):
    def __init__(self):
        self.file = open('njupt.txt','w')
    def process_item(self, item, spider):
        self.file.write(item['news_title'])
        self.file.write("\n")
        self.file.write(item['news_date'])
        self.file.write("\n")
        self.file.write(item['news_url'])
        self.file.write("\n")
        return item
