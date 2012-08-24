#!/usr/bin/env python
#-*- coding:utf-8 -*-
accounts_here = [
  {"username":'00000','password':'00000'},
]
import urllib
import urllib2
import cookielib
import json
import re,time,os,random
class Log:
  def _(self,s):
    try:
      return s.decode('utf8')
    except:
      return s

  def __init__(self):
    self.PATH=os.path.abspath(os.path.expanduser('.'))
    self.fd=open(self.PATH+"/log.tieba.txt",'a')
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    self.log("## %s"%t)
  def log(self,*args):
    for i in args:
      print(self._(i))
      self.fd.write(i)
      self.fd.write("\n")

class TieBa:
  def __init__(self,username,password):
    self.username=username.decode("utf8").encode("gbk")
    self.password=password
    cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686)')]
    urllib2.install_opener(self.opener)

  def urlopen(self,*args):
    try:
      if len(args)==1:
        fd=urllib2.urlopen(args[0])
      else:
        req = urllib2.Request(args[0], urllib.urlencode(args[1]))
        fd = urllib2.urlopen(req)
      return fd.read()
    except urllib2.HTTPError:
      l.log('发生错误，一秒钟后重试.')
      time.sleep(1)
      if len(args)>1 and 'tbs' in args[1]:
        if 'tid' in args[1]:
          args[1]['tbs']=self.getTbs(args[1]['tid'])
        else:
          args[1]['tbs']=self.getTbs()
      self.urlopen(*args)


  def getFid(self):
    page = self.urlopen(self.tb_url)
    fid=re.findall("fid:'(\d+)'",page)
    if fid==[]:
      l.log('获取fid失败一秒钟后重新获取.')
      time.sleep(1)
      return self.getFid()
    else:
      return fid[0]


  def getTbs(self,tid=None):
    if tid:
      page = self.urlopen("http://tieba.baidu.com/p/%s"%tid)
      l.log ("http://tieba.baidu.com/p/%s"%tid)
      tbs=re.findall("'tbs'  : \"(\w+)\"",page)[0]
    else:
      page = self.urlopen(self.tb_url)
      tbs=re.findall('PageData.tbs = "(\w+)"',page)[0]

    return tbs

  def sign(self):
    sign_url="http://tieba.baidu.com/sign/add"
    data={'ie':'utf-8','kw':self.kw}
    data['tbs']=self.getTbs()
    res = self.urlopen(sign_url,data)
    try:
      res = json.loads(res)
    except:
      pass
    if not res or res['error']!='':
      l.log ('签到失败')
    else:
      l.log ('签到成功','今日本吧第 %d 个签到'%res['data']['finfo']['current_rank_info']['sign_count'])

  def getContent(self):
    contents=['houhou','kankan','heihei']
    return random.sample(contents,1)[0]

  def reply(self,tid):
    if tid.__class__==[].__class__:
      for i in tid:
        self.reply(i)
      return
    
    reply_url="http://tieba.baidu.com/f/commit/post/add"
    data={
        'kw':self.kw,'ie':'utf-8','rich_text':'1','anonymous':'0',
        'content':self.getContent(),
        'fid':self.fid,
        'tid':tid
        }
    data['tbs']=self.getTbs(tid)
    fd = self.urlopen(reply_url,data)

  def login(self):
    def post():
      url = 'https://passport.baidu.com/v2/api/?login'
      page = self.urlopen(url,data)

    data={"username":self.username,"password":self.password,"verifycode":'',
        "mem_pass":"on","charset":"GBK","isPhone":"false","index":"0",
        "safeflg":"0","staticpage":"http://tieba.baidu.com/tb/v2Jump.html",
          "loginType":"1","tpl":"tb","codestring":'',
          "callback":"parent.bdPass.api.loginLite._submitCallBack"}

    post()
    token_url="https://passport.baidu.com/v2/api/?loginliteinfo&username=%s&isPhone=false&tpl=tb&immediatelySubmit=false&index=0&t=1345615911499"%self.username
    token_page=self.urlopen(token_url)
    data["token"]=re.findall("token:'(\w+)'" ,token_page)[0]
    post()

    return True

  def getTopics(self):
    page=self.urlopen(self.tb_url)
    tids=re.findall('<a href="/p/(\d+)" target="_blank" class="\w+">.+</a>',page)
    return tids

  def enter(self,tb_url):
    if tb_url.startswith('http://'):
      self.tb_url=tb_url
    else:
      self.tb_url="http://tieba.baidu.com%s"%tb_url
    self.fid=self.getFid()
    self.kw=re.findall("kw=([%\w]+)",self.tb_url)[0]
    self.kw=urllib.unquote(self.kw).decode("gbk").encode("u8")

    l.log ('> 进入贴吧 %s'%self.kw)

  def getTibBas(self):
    page=self.urlopen('http://tieba.baidu.com/')
    return re.findall('<a class="j_ba_link often_forum_link" forum-id="\d+" forum=".+" href="(.+)" target="_blank"',page)

if __name__ == '__main__':
  l=Log()
  for a in accounts_here:
    t = TieBa(a['username'],a['password'])
    if t.login():
      l.log('%s 登陆成功'%t.username.decode("gbk").encode("u8"))
      print 'DEBUG',t.getTibBas()
      for i in t.getTibBas():
        t.enter(i)
        # h.reply(h.getTopics()[3:6])
        t.sign()
  raw_input('press enter to continue.')
