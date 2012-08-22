#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
import json
import re,time,os,random
class Log:
  def __init__(self):
    self.PATH=os.path.abspath(os.path.expanduser('.'))
    self.fd=open(self.PATH+"/log.txt",'a')
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    self.log("## %s"%t,False)
  def log(self,s,indent=True):
    if indent:
      s="  %s"%s
    print(s.decode("u8"))
    self.fd.write(s)
    self.fd.write("\n")

class TieBa:
  def __init__(self,username,password):
    self.username=username
    self.password=password
    cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(self.opener)
    self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686)')]


  def getFid(self):
    page = urllib2.urlopen(self.tb_url).read()
    return re.findall("fid:'(\d+)'",page)[0]

  def getTbs(self,tid=None):
    if tid:
      page = urllib2.urlopen("http://tieba.baidu.com/p/%s"%tid).read()
      print "http://tieba.baidu.com/p/%s"%tid
      tbs=re.findall("'tbs'  : \"(\w+)\"",page)[0]
    else:
      page = urllib2.urlopen(self.tb_url).read()
      tbs=re.findall('PageData.tbs = "(\w+)"',page)[0]

    return tbs

  def sign(self):
    sign_url="http://tieba.baidu.com/sign/add"
    data={'ie':'utf-8','kw':self.kw}
    data['tbs']=self.getTbs()
    req = urllib2.Request(sign_url, urllib.urlencode(data))
    res = self.opener.open(req).read()
    res = json.loads(res)
    if res['error']=='':
      print '签到成功','今日本吧第 %d 个签到'%res['data']['finfo']['current_rank_info']['sign_count']
    else:
      print '签到失败'

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
        'content':'houhou',
        'fid':self.fid,
        'tid':tid
        }
    data['tbs']=self.getTbs(tid)
    req = urllib2.Request(reply_url, urllib.urlencode(data))
    fd = self.opener.open(req)

  def login(self):
    def post():
      url = 'https://passport.baidu.com/v2/api/?login'
      req = urllib2.Request(url, urllib.urlencode(data))
      try:
        fd = self.opener.open(req)
      except Exception, e:
        return False
      res=fd.read()
      fd.close()

    data={"username":self.username,"password":self.password,"verifycode":'',
        "mem_pass":"on","charset":"GBK","isPhone":"false","index":"0",
        "safeflg":"0","staticpage":"http://tieba.baidu.com/tb/v2Jump.html",
          "loginType":"1","tpl":"tb","codestring":'',
          "callback":"parent.bdPass.api.loginLite._submitCallBack"}

    post()
    token_url="https://passport.baidu.com/v2/api/?loginliteinfo&username=%s&isPhone=false&tpl=tb&immediatelySubmit=false&index=0&t=1345615911499"%self.username
    token_page=urllib2.urlopen(token_url).read()
    data["token"]=re.findall("token:'(\w+)'" ,token_page)[0]
    post()

    return True

  def getTopics(self):
    page=urllib2.urlopen(self.tb_url).read()

    tids=re.findall('<a href="/p/(\d+)" target="_blank" class="\w+">.+</a>',page)
    print tids
    return tids

  def enter(self,tb_url):
    if tb_url.startswith('http://'):
      self.tb_url=tb_url
    else:
      self.tb_url="http://tieba.baidu.com%s"%tb_url
    self.fid=self.getFid()
    self.kw=re.findall("kw=([%\w]+)",self.tb_url)[0]
    self.kw=urllib.unquote(self.kw).decode("gbk").encode("u8")

    print '> 进入贴吧',self.kw

  def getTibBas(self):
    page=urllib2.urlopen('http://tieba.baidu.com/').read()
    return re.findall('<a class="j_ba_link often_forum_link" forum-id="\d+" forum=".+" href="(.+)" target="_blank">',page)

if __name__ == '__main__':
    h = TieBa('username','password')
    if h.login():
      print('登陆成功')
      for i in h.getTibBas():
        h.enter(i)
        h.sign()
