# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json

class DmozPipeline(object):
    def __init__(self):
        self.file = open('dmoz.txt','w')
    def process_item(self, item, spider):
        self.file.write(item['title'][0])
        self.file.write("\t")
        self.file.write(item['link'][0])
        self.file.write("\t")
        s = item['desc'][1].strip()
        s = s.replace('\n',' ') # rm newline in the middle of a sentence
        s = s.replace('\r','') # rm newline in the middle of a sentence
        self.file.write(s)
        self.file.write("\n")
        return item
