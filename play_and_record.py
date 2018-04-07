#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 应该建立一个log文件，然后，里面有两个队列，
# 一个是已经完成的音频列表一个是未完成的音频列表。可以中途断开继续。

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


# global vars

music_files=[]
fileSource="./"
fileDest="./Output/"
record_stop_enable = 0
NUM_SAMPLES = 2000
program_flag_disable = 0
thread1=0
thread2=0


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

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

def log_file(string):
    global fileDest
    if fileDest[-1] =='/':
        filename = fileDest + "log_file.txt"
    f = open(filename,'a+')
    f.write(TimeStamps()+"  "+string+"\n")
    f.close()

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
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        os.makedirs(path)
        log_file(path+' 创建成功')
        return True
    else:
        log_file (path+' 目录已存在')
        return False

def HeadThink():
    '''
    决定播放
    '''
    global record_stop_enable
    global fileSource
    global fileDest
    global music_files
    global thread1
    global thread2
    global program_flag_disable
    nchannels , framerate , sampwidth = MakeChoice()
    # 得到音乐列表
    FileList(fileSource)
    mkdir(fileDest)
    count = len(music_files)
    thread3 = MyThread(GetChThread, None , GetChThread.__name__)
    thread3.start()
    for music in music_files:
        newFileName = GenerateNewFileName(music)
        log_file("==>start playing")
        thread1 = MyThread(PlayMusic, (music,), PlayMusic.__name__)
        thread2 = MyThread(my_record,(newFileName , framerate, nchannels, sampwidth,), my_record.__name__)
        thread1.setDaemon(True)
        thread2.setDaemon(True)
        thread2.start()
        log_file("record is recording")
        time.sleep(3)# 防止出现播放错误
        thread1.start()
        log_file("play is playing")
        thread1.join()
        log_file("play is end")
        record_stop_enable = 1
        thread2.join()
        if program_flag_disable:
            log_file("==> 提前结束程序")
            break
        log_file("==>record is end")
    log_file("结束程序")

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
    #log_file ("framerate %d nchannels %d sampwidth %d nframes %d"%(framerate,nchannels,sampwidth,nframes))
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
    cmd = 'play ' + filename
    log_file(cmd)
    os.system(cmd)

def PlayMP3(filename):
    cmd = 'play ' + filename
    os.system(cmd)

def GetChThread():
    global record_stop_enable
    global thread1
    global thread2
    global program_flag_disable
    while True:
        if _GetchUnix().__call__() == 'q':
            print("key q is pressed!")
            #os.kill()
            #sys.exit()
            #os._exit()
            #exit()
            program_flag_disable = 1
            #if thread1.isAlive():
            #    os.system("killall play")
            #    stop_thread(thread1)
            #if thread2.isAlive():
            #    stop_thread(thread2)
            #program_flag_disable = 1
            break

def save_wave_file(filename, data, framerate, channels, sampwidth):
    '''save the date to the wavfile'''
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()
    (filepath,tempfilename) = os.path.split(filename)
    mkdir(fileDest+filepath)
    cmd = "mv "+filename+" "+fileDest+filepath
    print cmd
    os.system(cmd)

def my_record(filename, framerate, channels, sampwidth):
    global record_stop_enable
    pa=PyAudio()
    stream=pa.open(format = paInt16,channels=channels,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    my_buf=[]
    log_file('Record Media.')
    while True:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        #log_file(".")
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
    #log_file_file_name()
    #PlayMusic(u"./kanong.wav")
    HeadThink()
    #my_record("helloworld.wav",16000,2,2)
    #log_file("fdafdsafds")
    #record_stop_enable = 1
    #MakeChoice()
    #PlayMP3("kanong.mp3")
    #FileList("./")
    #print("11111")
    #thread3 = MyThread(GetChThread, None , GetChThread.__name__)
    #thread3.start()
    #print("11111")
