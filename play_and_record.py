#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 应该建立一个log文件，然后，里面有两个队列，
# 一个是已经完成的音频列表一个是未完成的音频列表。可以中途断开继续。

# 打印混乱
import time
import wave
from pyaudio import PyAudio,paInt16
import pyaudio
import os
import thread
import threading
from time import sleep, ctime
import datetime
import getopt
import sys
import inspect
import ctypes
import logging

# global vars

music_files = []
fileSource = "./"
fileDest = "./Output/"
record_stop_enable = 0
NUM_SAMPLES = 2000
program_flag_disable = 0
thread1 = 0
thread2 = 0
logger = None

def MyLogging(filepath):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler(filepath+"log.txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # let the log print ahead of you
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    logger.addHandler(handler)
    logger.addHandler(console)
    logger.info("Start to log")

def FileExtension(path):
    return os.path.splitext(path)[1]

def FileList(filepath):
    '''
    打印目录下的所有的文件名称．
    '''
    for fpathe,dirs,fs in os.walk(filepath):
        for f in fs:
            if FileExtension(f) == ".wav" or FileExtension(f) == ".mp3":
                music_files.append(os.path.join(fpathe, f))
                #print os.path.join(fpathe, f)

def Fifo(RW):
    global fileDest
    global music_files
    if fileDest[-1] =='/':
        filename = fileDest + "fifo.txt"
    else:
        filename = fileDest + '/' + "fifo.txt"
    if (RW == "write"):
        f = open(filename,'w')
        f.write(" ".join(music_files))# list >>> str
        f.close()
    elif (RW == "read"):
        f = open(filename,'r')
        string = f.readline()
        string = string.split()# str >>> list
        f.close()
        print string
        return string

class MyThread(threading.Thread):

    def __init__(self,func,args,name):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.args=args

    def run(self):
        if self.args == None:
            apply(self.func)
        else:
            apply(self.func,self.args)

def GenerateNewFileName(oldFileName):
    if FileExtension(oldFileName) == ".mp3":
        return  oldFileName.replace(".mp3","_" + TimeStamps() + ".wav")
    if FileExtension(oldFileName) == ".wav":
        return oldFileName.replace(".wav","_" + TimeStamps() + ".wav")

def mkdir(path):
    # 去除首位空格
    global logger
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        print(path+' 创建成功')
        return True
    else:
        print (path+' 目录已存在')
        return False

def JudjeTheLogFileExits():
    global fileDest
    if fileDest[-1] =='/':
        filename = fileDest + "fifo.txt"
    else:
        filename = fileDest + '/' + "fifo.txt"

    if os.path.exists(filename):
        message = 'OK, the "%s" file exists.'
        return True
    else:
        message = "Sorry, I cannot find the "%s" file."
        print message % filename
        return False


def HeadThink():
    '''
    Decide to speak and listen
    '''
    global record_stop_enable
    global fileSource
    global fileDest
    global music_files
    global thread1
    global thread2
    global program_flag_disable
    global logger
    nchannels , framerate , sampwidth = MakeChoice()
    # 得到音乐列表
    FileList(fileSource)
    if(JudjeTheLogFileExits())
        music_files = Fifo("read")
    mkdir(fileDest)
    MyLogging(fileDest)
    count = len(music_files)
    #thread3 = MyThread(GetChThread, None , GetChThread.__name__)
    #thread3.start()
    for music in music_files:
        newFileName = GenerateNewFileName(music)
        logger.info("start playing")
        thread1 = MyThread(PlayMusic, (music,), PlayMusic.__name__)
        thread2 = MyThread(my_record,(newFileName , framerate, nchannels, sampwidth,), my_record.__name__)
        thread1.setDaemon(True)
        thread2.setDaemon(True)
        thread2.start()
        logger.info("record is recording")
        time.sleep(2)# 防止出现播放错误
        thread1.start()
        logger.info("play is playing")
        thread1.join()
        logger.info("play is end")
        record_stop_enable = 1
        thread2.join()
        logger.info("record is end")
        logger.info("sync the log file")
        
        if program_flag_disable:
            logger.info("kill the program in advance.")
            break
    logger.info("program is stop")

def TimeStamps():
    t = time.time()
    return datetime.datetime.now().strftime('%m-%d_%H:%M')

def MakeChoice():
    # 默认的参数
    global fileSource
    global fileDest
    channels=4
    framerate=16000
    sampwidth=2

    opts, args = getopt.getopt(sys.argv[1:], "s:d:c:f:w:h" ,["sourcefile=",\
        "destinationfile=","channels=","framerate=","sampwidth=","help"])
    for op, value in opts:
        if op == "-s":
            fileSource = value
        elif op == "-d":
            fileDest = value
        elif op == "-c":
            channels = int(value)
        elif op == "-f":
            framerate = int(value)
        elif op == '-w':
            sampwidth = int(value)
        elif op == "-h":
            Usage()
            sys.exit()
        else:
            Usage()
            sys.exit()
    return channels, framerate, sampwidth

def PlayWav(filename):
    waveFile = wave.open(filename, 'rb')
    params = waveFile.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    voiceCard = pyaudio.PyAudio()
    chunk = 1024
    #打开声音输出流
    stream = voiceCard.open(format = voiceCard.get_format_from_width(sampwidth),
                     channels = nchannels,
                     rate = framerate,
                     output = True)

    #写声音输出流到声卡进行播放
    data = waveFile.readframes(chunk)
    while True:
        data = waveFile.readframes(chunk)
        if data == b'':
            waveFile.close()
            #stop stream
            stream.stop_stream()
            stream.close()
            #close PyAudio
            voiceCard.terminate()
            break
        stream.write(data)

def PlayMusic(filename):
    global logger
    cmd = 'play ' + filename
    logger.info(cmd)
    os.system(cmd)

def PlayMP3(filename):
    global logger
    cmd = 'play ' + filename
    logger.info(cmd)
    os.system(cmd)

def GetChThread():
    ''' 这个会导致终端乱码'''
    global program_flag_disable
    while True:
        if _GetchUnix().__call__() == 'q':
            print("key q is pressed!")
            program_flag_disable = 1
            break

def save_wave_file(filename, data, framerate, channels, sampwidth):
    '''save the date to the wavfile'''
    global logger
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()
    (filepath,tempfilename) = os.path.split(filename)
    mkdir(fileDest+filepath)
    cmd = "mv "+filename+" "+fileDest+filepath
    logger.info(cmd)
    os.system(cmd)

def my_record(filename, framerate, channels, sampwidth):
    global record_stop_enable
    global logger
    pa=PyAudio()
    stream=pa.open(format = paInt16,channels=channels,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    my_buf=[]
    logger.info('Record Media.')
    while True:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        #logger.info(".")
        if record_stop_enable:
            record_stop_enable = 0
            break
    save_wave_file(filename, my_buf, framerate, channels, sampwidth)
    stream.close()

def Usage():
    print("    Please use `python2.7 play_and_record.py -fs <file_source> -fd <file_distination> -fr <framerate>")
    print("          -ch <channels> -sw <sampwidth> -h <for_help>'")
    print("    If you want to kill the program,press key ‘q’.")
    print("    Example:")
    print("        python2.7 play_and_record.py -fs ./ -fd ./hellofile -fr 16000 -ch 4 -sw 2")

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

if __name__ == "__main__":
    #HeadThink()
    FileList(fileSource)
    Fifo("write")
    Fifo("read")


