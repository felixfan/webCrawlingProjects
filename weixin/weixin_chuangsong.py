# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
 
import spynner
import urllib2
from BeautifulSoup import BeautifulSoup
import os

'''
通过公众号id返回所有文章的页数
'''
def get_pages(gzh_id):
	pages = [0]
	gzh_url = "http://chuansong.me/account/" + gzh_id
	headers = { 'User-Agent' : 'Mozilla/5.0' }
	request = urllib2.Request(gzh_url, None, headers)
	soup = BeautifulSoup(urllib2.urlopen(request).read())
	for link in soup.findAll("a"):
		urls = link.get('href')
		surls = str(urls)
		if -1 != surls.find('start='):
			arr = surls.split('start=')
			if not int(arr[1]) in pages:
				pages.append(int(arr[1]))
	max_s = max(pages)
	step = pages[1]
	for i in xrange(0, max_s, step):
		if not i in pages:
			pages.append(i)
	return sorted(pages)

'''
通过公众号id及起文件号返回该页内所有文章的网址
'''
def get_articles_url_of_one_page(gzh_id, start):
	a_urls = []
	page_url = "http://chuansong.me/account/" + str(gzh_id) + "?start=" + str(start)
	print 'process: {}'.format(page_url)

	base_url = 'http://chuansong.me'

	headers = { 'User-Agent' : 'Mozilla/5.0' }
	request = urllib2.Request(page_url, None, headers)
	soup = BeautifulSoup(urllib2.urlopen(request).read())

	for link in soup.findAll("h2"):
		a_url = base_url + str(unicode(link.a['href']))
		a_urls.append(a_url)

	return a_urls

'''
通过公众号id返回所有文章的网址
'''
def get_articles_url(gzh_id):
	all_urls = []
	pages = get_pages(gzh_id)
	idx = 1
	n = len(pages)
	for page in pages:
		urls = get_articles_url_of_one_page(gzh_id, page)
		all_urls.extend(urls)
		print 'get urls for articles in page {} of {}'.format(idx, n)
		idx += 1
	return all_urls


'''
根据每篇文章的网址抓取文章的内容并存放在以文章标题为名字的txt文件里
'''
def get_content(a_url):
	headers = { 'User-Agent' : 'Mozilla/5.0' }
	request = urllib2.Request(a_url, None, headers)
	soup = BeautifulSoup(urllib2.urlopen(request).read())
	post_date = soup.find(id='post-date').string  # post_date is a NavigableString. 
	post_date = str(unicode(post_date))           # You can convert a NavigableString to a Unicode string with unicode()
	title = soup.find(id='activity-name').string
	title = str(unicode(title))
	title = title.strip()
	content = soup.find(id='js_content')
	fw = open(title + '.txt', 'w')
	fw.write('{}\n{}\n\n'.format(title, post_date))
	for c in content.findAll('section', {'class':'tn-Powered-by-XIUMI'}):
		fw.write(str(unicode(c.getText())))
		fw.write('\n\n')
	fw.close()

if __name__ == '__main__':
	# gzh_id = 'dongjian360' # gzh_name = '洞见知行'
	gzh_id = 'jiankangkp' # gzh_name = '健康不是闹着玩儿'
	pages = get_pages(gzh_id)
	urls = get_articles_url_of_one_page(gzh_id, pages[0])
	get_content(urls[0])
