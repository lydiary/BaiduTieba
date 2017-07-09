# -*- coding: utf-8 -*-
import urllib2
import re

#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

#百度贴吧爬虫类
class BDTB:

    #初始化，出入基地址，是否只看楼主的参数
    def __init__(self, baseUrl, seeLZ=1, floorTag='1'):
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz=' + str(seeLZ)
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        #楼层标号，初始为1
        self.floor = 1
        #默认的标题，如果没有成功获取到标题的话则会用这个标题
        self.defaultTitle = u"百度贴吧"
        #是否写入楼分隔符的标记
        self.floorTag = floorTag

    #传入页码，获取该页帖子的代码
    def getPage(self, pageNum):
        try:
            url = self.baseURL + self.seeLZ + '&p=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            #print(response.read())
            return response.read()
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print(u'连接百度贴吧失败，错误原因：', e.reason)
                return None

    #获取贴子标题
    def getTitle(self, page):
        pattern = re.compile('h3 class="core_title_txt pull-left text-overflow.*?>(.*?)</h3>', re.S)
        result = re.search(pattern, page)
        if result:
            #print(result.group(1))
            return result.group(1).strip()
        else:
            return None

    #获取帖子一共有多少页
    def getPageNum(self, page):
        pattern = re.compile('<li class="l_reply_num".*?</span>.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            #print(result.group(1)) #测试输出
            return result.group(1).strip()
        else:
            return None

    #获取每一层的内容，传入页面内容
    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        contents = []
        for item in items:
            content = '\n' + self.tool.replace(item) + '\n'
            contents.append(content)
        return contents

    def setFileTitle(self, title):
        #如果标题不是为None，即成功获取到标题
        if title is not None:
            self.file = open(title + ".txt","w+")
        else:
            self.file = open(self.defaultTitle + ".txt", "w+")

    #将数据写入文件
    def writeData(self, contents):
        for content in contents:
            if self.floorTag == '1':
                #楼之间的分隔符
                floorLine = '<%d 楼------------------------------------------------------------------------------->' % self.floor
                self.file.write(floorLine)
            self.file.write(content)
            self.floor += 1

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)

        if pageNum == None:
            print('url已经失效，请重试。')
            return

        try:
            print('该帖子共有：%s页' % pageNum)
            for i in range(1, int(pageNum) + 1):
                print('正在写入第%d页数据' % i)
                page = self.getPage(i)
                contents = self.getContent(page)
                self.writeData(contents)
        except IOError, e:
            print('写入异常，错误原因： %s' % e.message)
        finally:
            print('写入任务完成')
        

if __name__ == '__main__':
    print u"请输入帖子代号"
    baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
    seeLZ = raw_input("是否只获取楼主发言，是输入1，否输入0\n")
    floorTag = raw_input("是否写入楼层信息，是输入1，否输入0\n")
    bdtb = BDTB(baseURL,seeLZ,floorTag)
    bdtb.start()