#-*-coding:utf8-*-
 
import re
import string
import requests
import sys, os
import urllib, urllib2
from bs4 import BeautifulSoup
from lxml import etree
import functools
 
reload(sys) 
sys.setdefaultencoding('utf-8')

cookie = {"Cookie": "yourCookie"}

'''
输入要爬取的微博用户的userID
输出该用户的所有微博内容:
 - 文字内容保存到以userID.txt命名文本文件中
 - 所有图片网址保存在userID_img_url.txt
 - 所有高清原图保存在userID_weibo_image文件夹中

1）首先我们要获得自己的cookie，这里只说chrome的获取方法:
  用chrome打开新浪微博移动端
  调出开发者工具
  点开Network，将Preserve log选项选中
  输入账号密码，登录新浪微博
  找到m.weibo.cn->Headers->Cookie，
  把cookie复制到代码中的yourCookie处  (weibo_spider.py文件第15行)
2）然后再获取你想爬取的用户的user_id，
  点开用户主页，地址栏里面那个号码就是user_id
3）运行：
  python weibo_spider.py user_id
  e.g. python weibo_spider.py 1878972254
'''

#### help function
def download_img(imgURL, localDir):
  '''
  urllib.urlretrieve(imgURL, filename) can NOT close the connection automatically
  so it will stop at downloading the image

  use requests to download image
  '''
  print 'downloading %s' % imgURL
  filename = imgURL.split('/')[-1]
  temp= localDir + '/%s' % filename
  r = requests.get(imgURL)
  f = open(temp,'w')
  f.write(r.content)
  f.close()

#### start here
if len(sys.argv) >= 2:
    user_id = (int)(sys.argv[1])
else:
    user_id = (int)(raw_input(u"请输入user_id: "))

url = 'http://weibo.cn/u/%d?filter=1&page=1' % user_id

#### get number of pages
html = requests.get(url, cookies = cookie).content
selector = etree.HTML(html)
pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
 
urllist_set = set()
word_count = 1
image_count = 1
 
print u'爬虫准备就绪...'
print 'There are total %d pages' % pageNum

result = ""
for page in range(1, pageNum+1):
  print 'process page %d' % page
  #获取lxml页面
  url = 'http://weibo.cn/u/%d?filter=1&page=%d' % (user_id, page) 
  lxml = requests.get(url, cookies = cookie).content 
  #文字爬取
  selector = etree.HTML(lxml)
  content = selector.xpath('//span[@class="ctt"]')
  for each in content:
    text = each.xpath('string(.)').encode('utf-8')
    if word_count >= 4:
      text = "%d :" % (word_count-3) + text + "\n\n"
    else :
      text = text + "\n\n"
    result = result + text
    word_count += 1
  #图片爬取
  soup = BeautifulSoup(lxml, "lxml")
  urllist = soup.find_all('a',href=re.compile(r'^http://weibo.cn/mblog/oripic',re.I))
  first = 0
  for imgurl in urllist:
    urllist_set.add(requests.get(imgurl['href'], cookies = cookie).url)
    image_count += 1
# output text
fo = open(str(user_id) + '.txt', "w")
fo.write(result)
fo.close()
word_path = os.getcwd() + '/%d%s' % (user_id, '.txt')
print u'文字微博爬取完毕, 共%d条, 保存路径%s' % (word_count-4, word_path)
# output image url
idx = 0
fo2 = open(str(user_id) + '_img_url.txt', "w")
for eachlink in urllist_set:
  link = eachlink + "\n"
  fo2.write(link)
  idx += 1
fo2.close()
img_path = os.getcwd()+'/%d%s' % (user_id, '_img_url.txt')
print u'图片链接爬取完毕, 共%d条, 保存路径%s' % (idx, img_path)
# download image
if not urllist_set:
  print u'该页面中不存在图片, 保存路径%s' % word_path
else:
  #下载图片
  image_path=os.getcwd() + '/' + str(user_id) + '_weibo_image'
  if os.path.exists(image_path) is False:
    os.mkdir(image_path)
  map(functools.partial(download_img, localDir=image_path), urllist_set)
  print u'图片下载完毕, 保存路径%s' % image_path
#### END ####
