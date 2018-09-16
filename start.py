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

def url2id(url):
    return uuid.uuid5(uuid.NAMESPACE_URL,url).__str__() 

#generate one m3u8's  download uris
def generatedownloaduris(dir, url):
    uri=url[:url.rindex('/')]
    downuri=[]
    with open(os.path.join(dir,'urilist.txt'), 'w') as f:
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
def mergets(tscachedir, mergedtsfilename):
    ls=[]
    with open(os.path.join(tscachedir,"urilist.txt")) as f:
        for line in f:
            if line.startswith('http') and line[len(line)-2:]=='s\n':
                ls.append(line[line.rindex('/'):][:-1]) 
    if(len(ls)>0):
        outputfile = open(mergedtsfilename, 'wb')
        for one in ls:         
            inputfile=open(os.path.join(tscachedir, one[1:]), 'rb')
            while 1:
                filebytes = inputfile.read(1024)
                if not filebytes: break
                outputfile.write(filebytes) 
            print "merged ",os.path.join(tscachedir, one[1:])
            inputfile.close()
        outputfile.flush()
        outputfile.close()
 

#convert ts stream file to mp4 file
def ts2mp4(outputfilename):
    cmd1 = "ffmpeg -y -i %s  -vcodec copy -acodec copy -vbsf h264_mp4toannexb %s"%(outputfilename+'.ts', outputfilename)
    os.system(cmd1)

#start download
def startdownload(tscachedir):
    #cmd = '%s'%('aria2c -c -x4 -d output1 -iurilist.txt -j10 --save-session=out.txt')
    #print cmd
    #p=subprocess.Popen(cmd,stdin = subprocess.PIPE, \
    #        stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
    #p.wait()
    #if p.returncode == 0:
    #    print "stdout:%s" %p.stdout.read()
        #pass
    cmd1 = "aria2c -c -x4 -d %s -i%s/urilist.txt -j10 --save-session=%s/out.txt  "%(tscachedir, tscachedir,tscachedir)
    os.system(cmd1)

#continue download
def continuedownload():
    with open('history.json') as json_file:  
        data = json.load(json_file)
        for p in data['Resources']:
            if p['state'] == 'downloading':
                filename = p['OPName'].decode('UTF-8').encode(sys.getfilesystemencoding())
                tempdir=os.path.join(os.path.dirname(filename), p['id'])
                ctask=os.path.join(tempdir,"out.txt")
                if(os.path.exists(ctask)):
                    cmd1="aria2c -c -i%s --save-session=%s"%(ctask,ctask)
                    os.system(cmd1)
                else:
                    startdownload(tempdir)
                mergets(tempdir, filename+".ts")
                ts2mp4(filename)
                setdownloadcomplete(p['URL'])
                purgetmpspace(tempdir, filename+'.ts')

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
        data['Resources'].append({  
            'id': url2id(uri),
            'URL': uri,
            'OPName': os.path.abspath(outputfilename).decode(sys.getfilesystemencoding()).encode('UTF-8'),
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

def setdownloadcomplete(uri):
    needwrite=False
    data={}
    with open('history.json', 'r+') as json_file: 
        data = json.load(json_file)
        for p in data['Resources']:
            print p['URL']
            print uri
            print
            if p['state'] == 'downloading' and p['URL'] == uri:
                p['state'] ='complete'
                needwrite=True
                break 

    if needwrite==True:    
        j=json.dumps(data, ensure_ascii=False, indent=4)
    #print j
        with open('history.json', 'w') as outfile:  
            print >> outfile, j

#purge tmp space
def purgetmpspace(tscachedir, mergedtsfilename):
    import shutil
    shutil.rmtree(tscachedir) 
    os.remove(mergedtsfilename)

#show uncomplete task
def showuncompletetask():
    pass

if __name__ == "__main__":
    reload(sys) 
    sys.setdefaultencoding('utf8')    #fix utf8 character coding bug of python2.7 
    showuncomplete, restoreuncomplete,url,outputfilename=parseargv()
    
    if showuncomplete == True:
        showuncompletetask()
        sys.exit(0)

    if restoreuncomplete == True:
        print "continue"
        continuedownload()
    
    if url != '' and outputfilename != '' :  
        generatedownloadhistory(url, outputfilename)
        print >> sys.stdout, "\033[1:37;42mGernerate Download History:\033[0m complete."
        
        outputdir=os.path.dirname(os.path.abspath(outputfilename)) 
        tempdir=os.path.join(outputdir,url2id(url))
        if not os.path.exists(tempdir): os.makedirs(tempdir)     

        generatedownloaduris(tempdir, url)
        print >> sys.stdout, "\033[1:37;42mGernerate Download URIS:\033[0m complete."

        startdownload(tempdir)
        print >> sys.stdout, "\033[1:37;42mAll TS files:\033[0m downloaded."
        
        #now merge ts file
        mergets(tempdir, outputfilename+'.ts')
        print >> sys.stdout, "\033[1:37;42mMerge all TS files:\033[0m complete."

        ts2mp4(outputfilename)

        print >> sys.stdout, "\033[1:37;42mMedia convert to MP4:\033[0m complete."
        
        setdownloadcomplete(url)

        purgetmpspace(tempdir, outputfilename+'.ts')
    
    print >> sys.stdout, "\033[1:37;42mAll task:\033[0m complete."

