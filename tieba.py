#!/usr/bin/env python
#-*- coding:utf-8 -*-
#email:kikyous@163.com

accounts_here = [
  {"username":'your_username','password':'your_password'},
  {"username":'your_anther_username','password':'your_password'},
]
import urllib
import urllib2
import cookielib
import json
import re,time,os,random,sys

# http://justpy.com/archives/199
def warp_gm_time(fun):
    def _warp_gm_time(*args):
        args=list(args)
        if args[0]>1899962739:
            args[0]=1899962739
        return fun(*args)
    if  hasattr( fun,'_is_hook'):
        return fun
    _warp_gm_time._is_hook=1
    return _warp_gm_time
time.gmtime=warp_gm_time(time.gmtime)

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(sys.executable)
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))
    return module_path
module_path=get_module_path()

class Log:
  if sys.platform.startswith('win'):
    @staticmethod
    def _(s):
      try:
        return s.decode('utf8')
      except:
        return s
  else:
    @staticmethod
    def _(s):
      return s

  @staticmethod
  def put(s):
    print(Log._(s))

  def __init__(self):
    self.PATH=sys.path[0]
    self.fd=open(self.PATH+"/log.tieba.txt",'a')
    t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    self.log("## %s"%t)

  def log(self,*args):
    for i in args:
      Log.put(i)
      self.fd.write(i)
      self.fd.write("\n")

class TieBa:
  def __init__(self,username,password):
    self.username=username
    self.password=password
    self.cookiepath="%s/tb.%s.cookie"%(module_path,username.decode('u8'))
    self.verifyimg="%s/verify.jpg"%(module_path)
    self.loaded=False
    self.cj = cookielib.LWPCookieJar(self.cookiepath)
    if os.path.isfile(self.cookiepath):
        self.cj.load(ignore_discard=True, ignore_expires=True)
        self.loaded=True
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
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
      return self.urlopen(*args)


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
    tbs=self.getTbs()
    if tbs==None:
      res=None
    else:
      data['tbs']=tbs
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
    if self.loaded:
  	return True
    def post():
      url = 'https://passport.baidu.com/v2/api/?login'
      page = self.urlopen(url,data)

    data={"username":self.username.decode("utf8").encode("gbk"),"password":self.password,"verifycode":'',
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
    self.cj.save()
    return re.findall('<a class="j_ba_link often_forum_link" forum-id="\d+" forum=".+" href="(.+)" target="_blank"',page)

class WapTieBa(TieBa):
  def __init__(self,username,password):
    TieBa.__init__(self,username,password)
    self.genimageurl='http://wappass.baidu.com/cgi-bin/genimage?'

  def login(self,data=None):
    if self.loaded:
  	return True

    url='http://wappass.baidu.com/passport/'
    if not data:
      data={
          'login_username':self.username,
          'login_loginpass':self.password,
          'uid':'wapp_1366340243477_203',
          'can_input':0,
          'ssid':000000,
          'login_username_input':0,
          'login':'yes',
          'tpl':'tb',
          'tn':'bdIndex'
          }
    fd=self.urlopen(url,data)
    if 'http-equiv="refresh"' in fd:
      return True
    elif self.genimageurl in fd:
      img=re.search('<img src="http://wappass.baidu.com/cgi-bin/genimage\?(\w+)"',fd).group(1)
      fp=self.urlopen(self.genimageurl+img)
      with open(self.verifyimg,'wb') as f:
        f.write(fp)
      try:
        import asubprocess
        subprocess.Popen(['xdg-open', self.verifyimg])
      except:
        Log.put("请打开 file://%s 查看验证码"%self.verifyimg)
      i=raw_input(Log._('请输入验证码:'))
      data['login_verifycode']=i.strip()
      data['login_bdverify']=img
      data['login']='vc'
      return self.login(data)

  def getTibBas(self):
    page=self.urlopen('http://wapp.baidu.com/mo/m?tn=bdFBW&tab=favorite')
    self.cj.save()
    return re.findall('<a href="/mo/[-_\w]+?/m\?kw=([%\w]+?)">.+?</a>',page)

  def enter(self,tb_kw):
    self.kw=urllib.unquote(tb_kw)
    self.tb_url='http://wapp.baidu.com/m?kw=%s'%self.kw
    l.log ('> 进入贴吧 %s'%self.kw)

  def getTbs(self,tid=None):
    if tid:
      page = self.urlopen("http://tieba.baidu.com/p/%s"%tid)
      l.log ("http://tieba.baidu.com/p/%s"%tid)
      tbs=re.findall("'tbs'  : \"(\w+)\"",page)
    else:
      page = self.urlopen(self.tb_url)
      tbs=re.findall('<input type="hidden" name="tbs" value="(\w+)"/>',page)
    if tbs==[]:
      return None
    return tbs[0]

if __name__ == '__main__':
  try:
    from accounts import accounts_here
  except:
    pass
  l=Log()
  for a in accounts_here:
    t = WapTieBa(a['username'],a['password'])
    if t.login():
      l.log('%s 登陆成功'%t.username)
      #print t.getTibBas();continue
      for i in t.getTibBas():
        t.enter(i)
        # t.reply(t.getTopics()[3:6])
        t.sign()
    else:
      l.log('%s 登陆失败'%t.username)

  if len(sys.argv) < 2:
    raw_input('\npress enter to continue.')
