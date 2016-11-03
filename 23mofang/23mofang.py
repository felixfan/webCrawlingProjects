#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import cookielib
from bs4 import BeautifulSoup
from urllib import urlencode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get_cookie(url, username, pwd):
	auth = {"username": username, "password": pwd}
	cookie = cookielib.CookieJar()
	handler = urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(handler)
	reponse = opener.open(url, urlencode(auth).encode("utf-8"))
	return cookie

def save_cookie_to_file(url, username, pwd, filename = 'cookie.txt'):
	auth = {"username": username, "password": pwd}
	cookie = cookielib.MozillaCookieJar(filename)
	handler = urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(handler)
	reponse = opener.open(url, urlencode(auth).encode("utf-8"))
	cookie.save(ignore_discard=True, ignore_expires=True)

def read_cookie_from_file(filename = 'cookie.txt'):
	cookie = cookielib.MozillaCookieJar()
	cookie.load(filename, ignore_discard=True, ignore_expires=True)
	return cookie

def get_disease_url(cookie):
	diseaseLink = {}
	base_url = "http://www.23mofang.com/report/"
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open("http://www.23mofang.com/report/disease")
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
	for link in soup.find_all('a'):
		href = str(link.get('href'))
		if href.startswith('disease/'):
			diseaseLink[base_url + href] = str(link.string)
	return diseaseLink

def get_trait_url(cookie):
	base_url = "http://www.23mofang.com/report/"
	traitLink = {}
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open("http://www.23mofang.com/report/trait")
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
	for link in soup.find_all('a'):
		href = str(link.get('href'))
		if href.startswith('trait/'):
			traitLink[base_url + href] = str(link.string)
	return traitLink
			
def get_disease_content(url, test, cookie):
	results = []
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open(url)
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
	tbody = soup.find('tbody')
	for tr in tbody.find_all('tr'):
		i = 0
		out = test + ','
		for td in tr.find_all('td'):
			i += 1
			if i == 1:
				for span in td.find_all('span'):
					if str(span.string) != '':
						tmp = str(span.string)
						tmp = tmp.replace('—', '')
						tmp = tmp.replace(' ', '')
						out += tmp
						out += ','
					else:
						out += 'NA'
						out += ','
				for gene in td.find_all('b'):
					if str(gene.string) != '':
						out += str(gene.string)
						out += ','
					else:
						out += 'NA'
						out += ','
			elif i == 2:
				out += str(td.string)
				out += ','
			elif i == 3:
				out += str(td.string)
		results.append(out)
	return results

def get_trait_content(url, test, cookie):
	results = []
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open(url)
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
	tbody = soup.find('tbody')
	for tr in tbody.find_all('tr'):
		out = test
		for td in tr.find_all('td'):
			out += ','
			out += str(td.string)
		results.append(out)
	return results

def get_disease(cookie, out='disease_SNPs.csv'):
	# 健康风险, 共80项
	diseaseLink = get_disease_url(cookie) 
	disease_out = ['检测项目名称,Chr,Cytoband,SNP,Gene,Genotype,风险倍数']
	for k, v in diseaseLink.items():
		print 'get genetics information for {} from {}'.format(v, k)
		r = (get_disease_content(k, v, cookie))
		disease_out.extend(r)
	f = open(out, 'w')
	for k in disease_out:
		f.write('{}\n'.format(k))
	f.close()

def get_trait(cookie, out='trait_SNPs.csv'):
	# 体质特征, 共34项
	traitLink = get_trait_url(cookie)
	trait_out = ['检测项目名称,Gene,SNP,Genotype,Description']
	for k, v in traitLink.items():
		print 'get genetics information for {} from {}'.format(v, k)
		r = (get_trait_content(k, v, cookie))
		trait_out.extend(r)
	f = open(out, 'w')
	for k in trait_out:
		f.write('{}\n'.format(k))
	f.close()

def get_disease_background(url, cookie):
 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open(url)
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')

	out = ''

	intro = soup.find('div', 'rptdtl-intro mb10')
	title = intro.find('h2', 'rptdtl-intro-title')
	out += str(title.string)

	explain = intro.find('div', 'rptdtl-intro-explain')
	out += '//'
	out += str(explain.p.string)

	highRisk = intro.find('div', 'rptdtl-buck rptdtl-buck-long fn-right')
	out += '//'
	i = 0
	for p in highRisk.find_all('p'):
		i += 1
		if i > 1:
			out += '||'
		out += str(p.string)

	result = soup.find('div', 'rptdtl-result mb10')
	researh = result.find('div', 'rptdtl-research-txt')
	out += '//'
	if researh.p:
		out += str(researh.p.string)
	else:
		out += 'None'

	relate = soup.find('div', 'rptdtl-relat mb10')
	for div in relate.find_all('div', 'rptdtl-panel-wrap'):
		out += '//'
		for div2 in div.find_all('div', 'rptdtl-panel-bd'):
			i = 0
			for p in div2.find_all('p'):
				i += 1
				if i > 1:
					out += '||'
		 		out += str(p.text)

	return out

def get_all_diseases_background(cookie, out='disease_background.txt'):
	diseaseLink = get_disease_url(cookie) 
	disease_out = ['检测项目名称//简介//高危人群//研究现状//疾病背景介绍//患病因素//症状//诊断']
	for k, v in diseaseLink.items():
		print 'get background for {} from {}'.format(v, k)
		disease_out.append(get_disease_background(k, cookie))
	f = open(out, 'w')
	for k in disease_out:
		f.write('{}\n'.format(k))
	f.close()

def get_all_traits_background(cookie, output='trait_background.txt'):
	traitLink = get_trait_url(cookie) 
	trait_out = ['检测项目名称//相关介绍']
	for k, v in traitLink.items():
		print 'get background for {} from {}'.format(v, k)
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
		reports = opener.open(k)
		soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
		out = v + '//'
		info = soup.find(id='subPart')
		i = 0
		for p in info.find_all('p'):
			i += 1
			if i > 1:
				out += '||'
			out += str(p.text).strip().replace('\n', ' ')
		trait_out.append(out)
	f = open(output, 'w')
	for k in trait_out:
		f.write('{}\n'.format(k))
	f.close()	

def get_cancer_infor(cookie, outfile='cancer_results.txt'):
	f = open(outfile, 'w')
	url = 'http://www.23mofang.com/report/inherit-tumour'

 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open(url)
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')

 	for div in soup.find_all('div', 'rptlist-item-wrap container'):
 		for tr in div.find_all('tr'):
 			i = 0
 			for td in tr.find_all('td'):
 				i += 1
 				if i > 1:
 					f.write('{}'.format('//'))
 				f.write('{}'.format(str(td.text)))
 			f.write('\n')
 		f.write('\n')
 	f.close()

def get_gene_url(cookie):
	out = {}
	url = 'http://www.23mofang.com/report/inherit-tumour'
 	base = 'http://www.23mofang.com/report/'

 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
	reports = opener.open(url)
	soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')

 	for div in soup.find_all('div', 'rptlist-item-wrap container'):
 		for g in div.find_all('a'):
 			href = base + str(g['href'])[2:]
 			if -1 != href.find('gene'):
 				out[href] = str(g.text)
 	return out

def get_gene_intro(cookie, outfile='cancer_gene_intro.txt'):
	urls = get_gene_url(cookie)
	f = open(outfile, 'w')
	f.write('{}//{}\n'.format('基因', '基因介绍'))

	for k,v in urls.items():
		print('get intro for {} from {}'.format(v, k))
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
		reports = opener.open(k)
		soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')

		info = soup.find(id='subPart')
		div = info.find('div', 'intro')
		f.write('{}//{}\n'.format(v, str(div.p.text).strip().replace('\n', ' ')))
	f.close()

def get_disease_ref(cookie, outfile='disease_reference.txt'):
	diseaseLink = get_disease_url(cookie) 
	disease_out = ['检测项目名称||检测对象||文献题目||文献链接||文献摘要']

	for k,v in diseaseLink.items():
		print 'get disease reference for {} from {}'.format(v, k)
	 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
		reports = opener.open(k)
		soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
		div = soup.find('div', 'rptdtl-locus-doc')
		for d in div.find_all('div'):
			out = v + '||' + str(d.b.text) + '||' + str(d.a.text) + '||' + str(d.a['href']) + '||' + str(d.p.text)
			disease_out.append(out)

	f = open(outfile, 'w')
	for k in disease_out:
		f.write('{}\n'.format(k))
	f.close()

def get_trait_ref(cookie, outfile='trait_reference.txt'):
	traitLink = get_trait_url(cookie) 
	trait_out = ['检测项目名称||期刊||题目||链接||作者']

	for k,v in traitLink.items():
		print 'get trait reference for {} from {}'.format(v, k)
	 	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
		reports = opener.open(k)
		soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')
		ref = soup.find('div', 'md-literature-pop-main')
		tbody = ref.tbody
		for tr in tbody.find_all('tr'):
			i = 0
			out = v
			for td in tr.find_all('td'):
				out += '||'
				out += str(td.text).strip()
				i += 1
				if i == 2:
					out += '||'
					out += str(td.a['href']).strip().replace(' ', '')
			trait_out.append(out)

	f = open(outfile, 'w')
	for k in trait_out:
		f.write('{}\n'.format(k))
	f.close()

def get_cancer_gene_ref(cookie, outfile='cancer_gene_reference.txt'):
	urls = get_gene_url(cookie)
	f = open(outfile, 'w')
	f.write('{}||{}||{}||{}||{}\n'.format('基因', '期刊', '题目', '链接', '作者'))

	for k,v in urls.items():
		print('get intro for {} from {}'.format(v, k))
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
		reports = opener.open(k)
		soup = BeautifulSoup(reports.read(), 'html.parser', from_encoding='UTF-8')

		ref = soup.find('div', 'md-literature-pop-main')
		tbody = ref.tbody
		for tr in tbody.find_all('tr'):
			i = 0
			out = v
			for td in tr.find_all('td'):
				out += '||'
				out += str(td.text).strip()
				i += 1
				if i == 2:
					out += '||'
					out += str(td.a['href']).strip().replace(' ', '')
			f.write('{}\n'.format(out))
	f.close()



if __name__ == '__main__':
	url = "http://www.23mofang.com/login"
	username = "" # your username
	pwd = ""      # your password
	cookie = get_cookie(url, username, pwd)

	if len(sys.argv) > 1 and sys.argv[1] == 'run':
		get_disease(cookie)
 		get_trait(cookie)
		get_all_diseases_background(cookie)
 		get_all_traits_background(cookie)
		get_cancer_infor(cookie)
 		get_gene_intro(cookie)
 		get_disease_ref(cookie)
 		get_trait_ref(cookie)
 		get_cancer_gene_ref(cookie)
 	else:
 		print 'usage: python 23mofang.py run'
