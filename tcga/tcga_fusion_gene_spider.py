#coding=utf-8
import spynner
import urllib2
from BeautifulSoup import BeautifulSoup
import datetime

'''
根据html的信息计算总页数
'''
def getNumOfPagesFromHtml(html):
	soup = BeautifulSoup(html)
	info = str(soup.find(id="fusions_info"))
	arr = info.split('>')
	ar = arr[1].split('<')
	a = ar[0].split()
	num = a[-2]
	num = int(num.replace(",", ""))
	if num % 10 == 0:
		return num / 10
	else:
		return num / 10 + 1


'''
提取html中fusion gene pair
'''
def extractFusionGenePairsFromHtml(html):
	fgp = []
	# 提取fusion gene pair
	soup = BeautifulSoup(html)
	for link in soup.findAll('a'):
		f_url = link.get('href')
		if f_url and -1 != f_url.find('geneNameA'):
			arr = f_url.split('?')
			fgp.append(arr[1].encode('utf-8'))
	return fgp

'''
提取GCTA数据库里的所有fusion gene pairs
'''
def gcta_spider(cancertype, tierclass):
	browser = spynner.Browser()
	browser.show()

	try:
		browser.load(url='http://54.84.12.177/PanCanFusV2/Fusions!cancerType')
		browser.load_jquery(True)
	except spynner.SpynnerTimeout:
		print 'Timeout.'
	else:
		# 输入搜索关键字
		# browser.wk_fill('select[id="cancerType"]', 'BRCA')
		browser.wk_select('[id="cancerType"]', cancertype)

		# browser.wk_fill('select[id="tier"]', 'tier1')
		browser.wk_select('[id="tier"]', tierclass)

		# 点击搜索按钮，并等待页面加载完毕  
		browser.wk_click('input[type="submit"]', wait_load=True)

		# 获取页面的HTML
		html = browser.html

		# get total pages
		pageNum = getNumOfPagesFromHtml(html)

		# first page
		p = 1
		fusionGenePairs = extractFusionGenePairsFromHtml(html)
		print 'processing page %d of %d' % (p, pageNum)

		# second to last page
		for i in xrange(1, pageNum):
			try:
				browser.wk_click('[id="fusions_next"]')
				html = browser.html
				tmp = extractFusionGenePairsFromHtml(html)
				fusionGenePairs.extend(tmp)
				tmp = []
				p = i + 1
				print 'processing page %d of %d' % (p, pageNum)
			except:
				print 'failed to click next page'
				break
			else:
				continue
	browser.close()
	return fusionGenePairs

'''
提取一对fusion gene pairs的注释信息
'''
def getFusionGenePairAnnot(pUrl):
	myurl = "http://54.84.12.177/PanCanFusV2/Fusions!fusion?%s" % pUrl
	soup = BeautifulSoup(urllib2.urlopen(myurl).read())
	annot = []
	for link in soup.findAll('a'):
		if link:
			url = link.get('href')
			if -1 != url.find('Fusion') and url.startswith('details'):
				cancer = url.split('Cancer=')[1].split('&')[0]
				sample = url.split('SampleID=')[1].split('&')[0]
				geneA = url.split('Gene_A=')[1].split('&')[0]
				geneB = url.split('Gene_B=')[1].split('&')[0]
				eValue = url.split('Evalue=')[1].split('&')[0]
				tier = url.split('tier=')[1].split('&')[0]
				frame = url.split('frame=')[1].split('&')[0]
				aChr = url.split('A_chr=')[1].split('&')[0]
				bChr = url.split('B_chr=')[1].split('&')[0]
				aStrand = url.split('A_strand=')[1].split('&')[0]
				bStrand = url.split('B_strand=')[1].split('&')[0]
				juncA = url.split('Junction_A=')[1].split('&')[0]
				juncB = url.split('Junction_B=')[1].split('&')[0]
				Discordant_n	= url.split('Discordant_n=')[1].split('&')[0]
				JSR_n = url.split('&JSR_n=')[1].split('&')[0]
				perfectJSR_n = url.split('perfectJSR_n=')[1].split('&')[0]

				fusionPair = "%s__%s" % (geneA, geneB)
				fivePrimeJunc = "Chr%s:%s/%s" % (aChr, juncA, aStrand)
				threePrimeJunc = "Chr%s:%s/%s" % (bChr, juncB, bStrand)

				tmp = (cancer, sample, geneA, geneB, fusionPair, eValue, tier, frame, fivePrimeJunc, threePrimeJunc, Discordant_n, JSR_n, perfectJSR_n)
				annot.append(tmp)
	return annot

if __name__ == '__main__':
	cancertype = ('BLCA', 'BRCA', 'GBM', 'HNSC', 'KIRC', 'LAML', 'LGG', 'LUAD', 'LUSC', 'OV', 'SKCM', 'THCA', 'PRAD', 'ACC', 'UCS', 'CESC', 'ESCA', 'READ', 'UVM','COAD')
	tierclass = ('tier1', 'tier2', 'tier3', 'tier4')
	
	# test
	# cancertype = ('BRCA',)
	# tierclass = ('tier4',)

	# get all fusion gene pairs
	allFusionGenePairs = []
	for c in cancertype:
		for t in tierclass:
			print 'cancer: %s\ttier: %s' % (c, t)
			fgp = gcta_spider(c, t)
			allFusionGenePairs.extend(fgp)
	records = len(allFusionGenePairs)
	allFusionGenePairs = set(allFusionGenePairs)

	print 'There are total %d cancers in %d different tiers' % (len(cancertype), len(tierclass))
	print 'There are total %d records' % records
	print 'There are total %d unique fusion gene pairs' % len(allFusionGenePairs)
	print '\nDownloading information for each pair of fusion genes\n'

	# get annotation for each fusion gene pair
	allAnnot = []
	for fgpURL in allFusionGenePairs:
		annot = getFusionGenePairAnnot(fgpURL)
		allAnnot.extend(annot)

	# write results to file
	## yyyymmdd format
	d = datetime.datetime.now()
	stime = str(d.year) + str(d.month) + str(d.day) + str(d.hour) + str(d.minute) + str(d.second)
	output = "tcga_fusion_genes_annot_%s.txt" % stime
	header = ("Cancer", "TCGA_Sample_ID", "Gene_A", "Gene_B", "Fusion_Pair", "E_Value", "Tier", "Frame", "5_Prime_Gene_Junction", "3_Prime_Gene_Junction", "Number_of_Discordant_Read _Pair", "Number_of_Junction_Spanning_Read", "Number_of_Perfect_Junction_Spanning_Read")
	f = open(output, 'w')
	for i in allAnnot:
		idx = 0
		for j in i:
			if idx == 0:
				f.write(j)
			else:
				f.write('\t%s' % j)
			idx += 1
		f.write('\n')
	f.close()
