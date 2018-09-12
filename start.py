#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import urllib,urllib2
import subprocess
import os
import sys,getopt
import json
from datetime import datetime
import uuid

#并行批量下载任务,用以提高网络较慢的网站的下载效率
#CTRL+C 退出下载之后断点续传
#aria2c -iurilist.txt -j10 --save-session=out.txt #使用最大10个并发下载urilist.txt中的下载文件
# CTL+c或者 aria2 退出时，所有的错误（error）/未完成（unfinished）下载将会保存到out.txt 文件中
#
#已测试清单:
#    2018ISC
#    url='http://live.us.sinaimg.cn/002CKdCnjx07nmuqwi3J070d01000w3E0k01.m3u8'
#    2018中国人工智能大会
#    url='http://live.us.sinaimg.cn/003KBuuJjx07mnPN1eFh070d01000pkH0k01.m3u8'
#    祈祷落幕时
#    url=http://youku163.zuida-bofang.com/20180804/10904_06d1f97f/800k/hls/index.m3u8
#    浪矢解忧杂货店.mp4
#    http://sohu.zuida-163sina.com/ppvod/4041E9CCBF3D7D59234D35F3E491599D.m3u8

class Usage(Exception):
    def __init__(self,msg=''):

        if msg != '':
            print >> sys.stderr, "\033[1:37;41mParamater Err:\033[0m %s"%msg
        print >> sys.stderr, "\033[1:37;42mUsage:\033[0m"
        print >> sys.stderr,  " "*4, "   -u \t m3u8 URL address,should be used with -o together"
        print >> sys.stderr,  " "*4, "   -o \t output media's name, should be used with -u together"
        print >> sys.stderr,  " "*4, "   -r \t restore last uncomplete task"
        print >> sys.stderr,  " "*4, "   -s \t show if exists uncomplete task"
        print >> sys.stderr,  " "*4, "   -h \t this message."
    

def parseargv(argv=None):
    showuncomplete, restoreuncomplete=False,False
    url,outputfilename='',''
    try:
        try:
            opts, args=getopt.getopt(sys.argv[1:], "hrsu:o:") 
            for op, value in opts:
                if op =="-u":
                    url=value
                elif op == "-o":
                    outputfilename=value
                elif op == "-r":
                    restoreuncomplete=True
                elif op == "-s":
                    showuncomplete=True
                elif op== "-h":
                    Usage()
                    sys.exit()
            if restoreuncomplete == False and showuncomplete == False:
                #开启新的下载任务
                if  len(sys.argv)!=5:
                    Usage()
                    sys.exit()
            elif showuncomplete == True:
                sys.exit()
                pass    #TODO: 显示上次没有完成的下载
            return showuncomplete, restoreuncomplete,url,outputfilename
        except getopt.error,msg:
            raise Usage(msg)
    except Usage:
        sys.exit(2)

#generate one m3u8's  download uris
def generatedownloaduris(url):
    uri=url[:url.rindex('/')]
    downuri=[]
    with open('urilist.txt', 'w') as f:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        res = res.read()
        lines = res.split("\n")
        
        for line in lines:
            if line.startswith('#E'):
                continue
            else:
                
                if len(line) > 0 :
                    if line.startswith('/') and len(uri)>7:
                        downuri.append('%s/%s\n'%(uri[:uri.find('/', 7)],line[1:]))
                    else:
                        downuri.append('%s/%s\n'%(uri,line))
                    #print('%s/%s\n'%(uri,line))
        f.writelines(downuri)

#merge ts file
def mergets():
    ls=[]
    with open("urilist.txt") as f:
        for line in f:
            if line.startswith('http') and line[len(line)-2:]=='s\n':
                ls.append(line[line.rindex('/'):][:-1]) 
    if(len(ls)>0):
        for one in ls:
            cmd1 = 'cat output1/%s >> tmp1.ts'%(one) 
            if os.system(cmd1) == 0:
                print "merged output1/", one
 

#convert ts stream file to mp4 file
def ts2mp4(outputfilename):
    cmd1 = "ffmpeg -y -i tmp1.ts -vcodec copy -acodec copy -vbsf h264_mp4toannexb "+outputfilename
    os.system(cmd1)

#continue download
def continuedownload(parameter_list):
    cmd1=''
    if os.path.exists("out.txt"):
        cmd1 = "aria2c -c -iout.txt -j10 --save-session=out.txt  "
    else:
        cmd1 = "aria2c -c -x4 -d output1 -iurilist.txt -j10 --save-session=out.txt  "
    os.system(cmd1)

#generate download history
#save this task to local json formatted file
#{
#   Resources:
#   [
#     {
#       id:GUID, 
#       URL:downloadurl,
#       OPName:outputfileName, 
#       timestamp:2018/08/11 16:10,
#       state:downloading/complete     
#     },
#     {
#       id:GUID, 
#       URL:downloadurl,
#       OPName:outputfileName, 
#       timestamp:2018/08/11 18:10,
#       state:downloading/complete
#     }
#   ]
# }
def generatedownloadhistory(uri, outputfilename):
    #查找URI是否存在 
    urlExitsInFile=False
    data={}
    data['Resources'] = []  
    try:
        with open("history.json", 'r') as history:
            data=json.load(history)
            for p in data['Resources']:
                if(p['URL'] == uri):
                    print('Hit History URL: ' + p['URL'])
                    urlExitsInFile = True
                    break
    except:
        pass
    if urlExitsInFile == False:
        id = uuid.uuid5(uuid.NAMESPACE_URL,uri) 
        data['Resources'].append({  
            'id': id.__str__(),
            'URL': uri,
            'OPName': outputfilename.decode(sys.getfilesystemencoding()).encode('UTF-8'),
            'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'state':'downloading'
        })
        #with open("history.json", "w") as history:
        #    json.dump(data, history, ensure_ascii=False)
        j = json.dumps(data, ensure_ascii=False, indent=4)
        with open('history.json', 'w') as outfile:  
            print >> outfile, j
    pass

#save download job
def savedownloadjob():
    pass

#start download
def startdownload():
    #cmd = '%s'%('aria2c -c -x4 -d output1 -iurilist.txt -j10 --save-session=out.txt')
    #print cmd
    #p=subprocess.Popen(cmd,stdin = subprocess.PIPE, \
    #        stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
    #p.wait()
    #if p.returncode == 0:
    #    print "stdout:%s" %p.stdout.read()
        #pass
    cmd1 = "aria2c -c -x4 -d output1 -iurilist.txt -j10 --save-session=out.txt  "
    os.system(cmd1)

#purge tmp space
def purgetmpspace():
    import shutil
    shutil.rmtree('./output1')
    #os.mkdir('./output1')  
    cmd1 = "del *.ts"
    os.system(cmd1)

#show uncomplete task
def showuncompletetask():
    pass

if __name__ == "__main__":
    reload(sys) 
    sys.setdefaultencoding('utf8')    #utf-8 python2.7 error
    showuncomplete, restoreuncomplete,url,outputfilename=parseargv()
    if showuncomplete == True:
        showuncompletetask()
        sys.exit(0)

    if restoreuncomplete == True:
        print "continue"
        continuedownload('')
    
    if url != '' and outputfilename != '' :        
        generatedownloadhistory(url, outputfilename)
        
        generatedownloaduris(url)
        startdownload()
    
    #now merge ts file
    mergets()

    filename='NONAME.mp4'
    if outputfilename!='' :
        filename = outputfilename
    else:
        data = {}
        with open('history.json') as json_file:  
            data = json.load(json_file)
            for p in data['Resources']:
                if p['state'] == 'downloading':
                    if p['OPName'] != '':
                        filename = p['OPName'].decode('UTF-8').encode(sys.getfilesystemencoding())
                    p['state'] ='complete'
                break

    ts2mp4(filename)

    
    with open('history.json', 'r+') as json_file: 
        data = json.load(json_file)
        if outputfilename!='':
            for p in data['Resources']:
                if p['state'] == 'downloading':
                    if p['OPName'] != '':
                        filename = p['OPName'].decode('UTF-8').encode(sys.getfilesystemencoding())
                    p['state'] ='complete' 
        
    j=json.dumps(data, ensure_ascii=False, indent=4)
    print j
    with open('history.json', 'w') as outfile:  
        print >> outfile, j

    purgetmpspace()
    
    print >> sys.stdout, "\033[1:37;42mDwonload:\033[0m complete."

