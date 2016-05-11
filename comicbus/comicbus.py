#coding=utf-8
import spynner
import sys
import os
from PyQt4.QtWebKit import QWebSettings # 用來設定 QtWebKit

'''
下载 http://www.comicbus.com/ 里面动画的图片
目前实现的是“美少女战士”第一卷
可以通过修改base_url和ch_no下载其它漫画及其它卷
reference: http://weijr-note.blogspot.hk/2014/11/blog-post.html
'''

# 建立浏览器
browser = spynner.Browser(debug_level=spynner.ERROR, debug_stream=sys.stderr)

# 打开浏览器
# browser.show() 

#  建立一个webview
browser.create_webview()
settings = browser.webview.settings()
# settings.setAttribute(QWebSettings.AutoLoadImages, False)      # 设定不要自动载入图片
settings.setAttribute(QWebSettings.JavaEnabled, False)           # 不需要Java
settings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)     # 节省dns花的时间
settings.setAttribute(QWebSettings.PrivateBrowsingEnabled, True) # 不需要浏览记录

# 美少女战士的url
base_url = 'http://v.comicbus.com/online/finance-389.html?ch='

# 美少女战士第一卷
ch_no = '1' #卷号
browser.load(base_url + ch_no)

# 漫画网址格式是base_url + 'M-N', 其中M,N是数字，分别是卷数及页数
# 找总页数
# 先用 runjs 跑 javascript 得到一个結果，再转成整数。
total_pages = browser.runjs('ps').toInt()[0] 

# 抓图：可以用 browser.download(img_url, outfd=fd) 下载
for page in range(1, total_pages+1):
	# 载入页面
    browser.load("{}{}-{}".format(base_url, ch_no, page))

    # 获取图片网址
    # 先用 runjs 跑 javascript 得到一个結果。 
	# 這个結果是一个 Qt (C++)物件，可能是數字、字串或者物件。
	# 因为我门要的是字符串，所以用　.toString 把它转成 Qt 字符串。
	# 最后，再用 str 转成Python 字串。
	# spynner 內建有 jquery，用這個个method 载入，比较方便。
    # img_url = str(browser.runjs('$("#TheImg").attr("src")').toString())
    img_url = str(browser.runjs('document.getElementById("TheImg").getAttribute("src")').toString())
    # print page, img_url

    # 下载到当前目录下，文件名为M-N.png
    with open("{}-{}.png".format(ch_no, page), "w") as f:
        browser.download(img_url, outfd=f)
        print "File saved in", os.getcwd()