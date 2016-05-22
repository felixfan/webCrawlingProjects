# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
 
import spynner
import urllib2
from BeautifulSoup import BeautifulSoup
import os

# 从搜狗微信抓取微信公众号的博文
# 试了几次后被block了，弹出验证码

'''
通过微信公众号返回公众号网址
'''
def get_gzh_url(gzh_name):
	browser = spynner.Browser()
	browser.show()
	wurl = unicode('http://weixin.sogou.com/weixin?type=1&query={}&ie=utf8&_sug_=n&_sug_type_='.format(gzh_name))
	try:
		browser.load(url=wurl)
	except spynner.SpynnerTimeout:
		print 'Timeout.'
	else:
		html = browser.html
		soup = BeautifulSoup(html)
		info = soup.find(id="sogou_vr_11002301_box_0")
		gzh_url = info.get('href')
		browser.close()
	return gzh_url

'''
通过公众号网址返回最近10天所有文章的网址
'''
def get_articles_url(gzh_url):
	a_urls = []
	base_url = "http://mp.weixin.qq.com"
	browser = spynner.Browser()
	browser.show()
	try:
		browser.load(url=gzh_url)
	except spynner.SpynnerTimeout:
		print 'Timeout.'
	else:
		html = browser.html
		soup = BeautifulSoup(html)
		for link in soup.findAll("h4"):
			f_url = link.get('hrefs')
			f_url = base_url + f_url
			a_urls.append(f_url)
		browser.close()
	return a_urls

'''
根据每篇文章的网址返回文章的日期
'''
def get_date(a_url):
	soup = BeautifulSoup(urllib2.urlopen(a_url).read())
	post_date = soup.find(id='post-date').string
	return post_date

'''
根据每篇文章的网址抓取文章的内容并存放在以文章标题为名字的txt文件里
'''
def get_content(a_url):
	soup = BeautifulSoup(urllib2.urlopen(a_url).read())
	post_date = soup.find(id='post-date').string  # post_date is a NavigableString. 
	post_date = str(unicode(post_date))           # You can convert a NavigableString to a Unicode string with unicode():
	title = soup.find(id='activity-name').string
	title = str(unicode(title))
	title = title.strip()
	content = soup.find(id='js_content')
	fw = open(title + '.txt', 'w')
	fw.write('{}\n{}\n\n'.format(title, post_date))
	for c in content.findAll('p'):
		fw.write(str(unicode(c.getText())))
		fw.write('\n\n')
	fw.close()

if __name__ == '__main__':
	# gzh_name = '洞见知行'
	gzh_name = '健康不是闹着玩儿'
	gzh_url = get_gzh_url(gzh_name)
	articles_url = get_articles_url(gzh_url)
	for r in articles_url:
		get_content(r)
		