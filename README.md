# real-m3u8-url-batch-downloader
this is a  m3u8 url batch download tool by a  python beginner.  Test in Windows, but support for linux and MacOS maye. Only for study.

```
**Usage**:
    -u       m3u8 URL address,should be used with -o together
    -o       output media's name, should be used with -u together
    -r       restore all uncomplete task
    -s       show all history tasks
    -h       this message.
```

for example, create a new online m3u8 download task, where m3u8 URI locate at http://live.us.sinaimg.cn/003KBuuJjx07mnPN1eFh070d01000pkH0k01.m3u8 , you could execute the following command in Windows original CMD shell or  nice console emulators, such as `cmder`:

`python start.py -u http://live.us.sinaimg.cn/003KBuuJjx07mnPN1eFh070d01000pkH0k01.m3u8 -o 2018ICS中国.mp4`



**Features:**

1. concurrence batch download online m3u8.

2. auto merge all TS files and convert to a single MP4 file, and support specify path.

3. continue download all uncomplete tasks.

   `python start.py -r`

4. save download list file(`history.json`) in UTF-8 Character coding,  and downloaded file name support UNICODE and ASCII by ` sys.getfilesystemcoding()`

5. show all download history
    `python start.py -s`

6. download split TS files and clear temp files and path automatically.



**For Windows User:**

you should download all .exe file in this Repo with start.py in same path.

**For Linux user:**

you should download and install `aria2`,  `FFmpeg`.

**For Mac user:**

should brew download and install `aria2`,`ffmpeg`.



**TODO**:

- [x] <del>show history task.</del>

- [ ] expose more aria2c control parameters to user, a new aria2c configure file maybe a good idea.

- [x] <del>change system command `rmdir, rm, del,cat `, path and somthing etc. to compatible with Mac or Linux systems.</del>

- [ ] sniffer or crawl method to get m3u8 URI easy.

- [ ] parse m3u8 format more **compatible**,refer to [globocom/*m3u8*](https://github.com/globocom/m3u8)

- [ ] parse URL more **comprehensive**,  refer to [**urlparse**](https://docs.python.org/2.7/library/urlparse.html) or [**urllib.parse**](https://docs.python.org/3/library/urllib.parse.html)

- [ ] refactoring  code with python3.

**More Reference**:

`aria2c` [https://aria2.github.io/](https://aria2.github.io/)

`FFmpeg` [http://ffmpeg.org/](http://ffmpeg.org/)


