# 下载新浪微博一个用户的微博内容及图片

## 1. 输入输出

* 输入要爬取的微博用户的userID
* 输出该用户的所有微博内容:
 - 文字内容保存到以userID.txt命名文本文件中
 - 所有图片网址保存在userID_img_url.txt
 - 所有高清原图保存在userID_weibo_image文件夹中

## 2. 使用说明

### 2.1 首先我们要获得自己的cookie，这里只说chrome的获取方法:

- 用chrome打开新浪微博移动端 (m.weibo.cn)
- 调出开发者工具
- 点开Network，将Preserve log选项选中
- 输入账号密码，登录新浪微博
- 找到m.weibo.cn->Headers->Cookie，
- 把cookie复制到代码中的yourCookie处  (weibo_spider.py文件第15行)

### 2.2 然后再获取你想爬取的用户的user_id

- 点开用户主页，地址栏里面那个号码就是user_id

### 2.3 运行

```
python weibo_spider.py user_id
```

例如抓取微博用户“我是cosplayer”的微博（http://m.weibo.cn/u/1878972254）

```
python weibo_spider.py 1878972254
```
