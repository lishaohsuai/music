#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 参考页面:https://www.cnblogs.com/xingshansi/p/6799994.html
# 参考页面：https://www.cnblogs.com/fnng/p/3691053.html

import time
import wave
from pyaudio import PyAudio,paInt16
import pyaudio
import os
import thread
import threading
from time import sleep, ctime
import getopt
import sys
import mp3play

filepath = './'
record_stop_enable=0
NUM_SAMPLES = 2000


def print_file_name():
    '''
    打印目录下的所有的文件名称．
    '''
    filename = os.listdir(filepath) # 得到文件夹下的所有的文件名
    for file in filename:
        print(file)

def log_file():
    pass

def exchange_voice_card():
    pass

class MyThread(threading.Thread):

    def __init__(self,func,args,name):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.args=args

    def run(self):
        apply(self.func,self.args)

def HeadThink():
    '''
    决定播放
    '''
    global record_stop_enable
    framerate =  16000
    nchannels =  4
    sampwidth =  2

    print("开始播放音乐")
    thread1 = MyThread(PlayMusic, ("kanong.wav",),PlayMusic.__name__)
    thread2 = MyThread(my_record,("helloworld.wav" , framerate, nchannels, sampwidth,), my_record.__name__)
    thread2.start()
    print("record is recording")
    sleep(3)# 防止出现播放错误
    thread1.start()
    print("play is playing")
    thread1.join()
    print("play is end")
    record_stop_enable = 1
    thread2.join()
    print("record is end")
    print("结束录音")

def MakeChoice():
    # 默认的参数
    fileSource="./"
    fileDest="./Output"
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
    #print fileSource,fileDest,channels,framerate
    #HeadThink()

def PlayWav(filename):
    waveFile = wave.open(filename, 'rb')
    params = waveFile.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    #print ("framerate %d nchannels %d sampwidth %d nframes %d"%(framerate,nchannels,sampwidth,nframes))
    voiceCard = pyaudio.PyAudio()
    chunk = 1024
    #打开声音输出流
    stream = voiceCard.open(format = voiceCard.get_format_from_width(sampwidth),
                     channels = nchannels,
                     rate = framerate,
                     output = True)

    #写声音输出流到声卡进行播放
    data = waveFile.readframes(chunk)
    i=1
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




def PlayMP3(filename):


def _GetChThread():
    global record_stop_enable
    while True:
        if _GetchUnix().__call__() == 'q':
            record_stop_enable = 1
            break

def save_wave_file(filename, data, framerate, channels, sampwidth):
    '''save the date to the wavfile'''
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()

def my_record(filename, framerate, channels, sampwidth):
    global record_stop_enable
    pa=PyAudio()
    stream=pa.open(format = paInt16,channels=channels,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    my_buf=[]
    print('Record Media.')
    while True:
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        #print(".")
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
    print("    Thinks for using ;)")

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

def InputKey():
    myStr = raw_input("Enter your input:")
    return myStr

def Main():

    if len(sys.argv) < 2:
        Usage()
        return False
    if len(sys.argv) == 2:
        if sys.argv[1] != "":
            gain = sys.argv[1]
        else:
            gain = "1"
    else:
        gain = "1"

    CheckFile(listfile,gain)
    print("Press 'm' to exit")
    while True:
        vad_key = _GetchUnix().__call__()
        if vad_key == 'w':
            kws_key = _GetchUnix().__call__()
            if kws_key == 'a':
                print("Hei,Start Record !")
                my_uuid = str(uuid.uuid1()).replace('-', '')
                wavfile = my_uuid
                wavfile += ".wav"
                my_record(wavfile)
                print ("Change Volume !")
                ChangeVolume(wavfile, "NEW_" + wavfile, gain)
                print ("Now Send To Cloud !")
                return True
            elif kws_key == 'q':
                pass
        elif vad_key == 'm':
            print ("See You !")
            return False


if __name__ == "__main__":
    #print_file_name()
    #PlayMusic(u"./kanong.wav")
    #HeadThink()
    #my_record("helloworld.wav",16000,2,2)
    #print("fdafdsafds")
    #record_stop_enable = 1
    MakeChoice()
