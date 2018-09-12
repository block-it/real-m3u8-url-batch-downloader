# real-m3u8-url-batch-downloader
this is a  m3u8 url batch download tool by a  python beginner.  Test in Windows, but support for linux and MacOS maye. Only for study.

**Usage**:
    -u       m3u8 URL address,should be used with -o together
    -o       output media's name, should be used with -u together
    -r       restore last uncomplete task
    -s       show if exists uncomplete task
    -h       this message.

for example, create a new online m3u8 download task, where m3u8 URI locate at http://live.us.sinaimg.cn/003KBuuJjx07mnPN1eFh070d01000pkH0k01.m3u8 , you could execute the following command in Windows original CMD shell or  nice console emulators, such as `cmder`:

python start.py -u http://live.us.sinaimg.cn/003KBuuJjx07mnPN1eFh070d01000pkH0k01.m3u8 -o 2018ICS中国.mp4



**For Windows User:**

you should download all .exe file in this Repo with start.py in same path.

**For Linux user:**

you should download and install `aria2c`,  `FFmpeg`.

**TODO**:

1. show uncomplete task.
2. expose more aria2c control parameters to user, a new aria2c configure file maybe a good idea.
3. change system call `rmdir, rm` to compatible witch Mac or Linux systems.
4. add sniffer or crawl method to make correct m3u8 URI easy.
5. parse m3u8 format more **compatible**,refer to [globocom/*m3u8*](https://github.com/globocom/m3u8)
6. parse URL more **comprehensive**,  refer to **urlparse** or [**urllib.parse**](https://docs.python.org/3/library/urllib.parse.html)
7. refactoring  code with python3.

**More Reference**:

`aria2c` [https://aria2.github.io/](https://aria2.github.io/)

`FFmpeg` [http://ffmpeg.org/](http://ffmpeg.org/)


