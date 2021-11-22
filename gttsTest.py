# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 21:57:15 2021

@author: upup5
"""
#http://yhhuang1966.blogspot.com/2017/08/google-gtts-api.html
#https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/372085/
from gtts import gTTS
from pygame import mixer
import tempfile

def speakChinese(_text):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts=gTTS(text=_text,lang='zh-TW')
        tts.save(f'{fp.name}.mp3')#要用fp.name存檔才可以在執行後自動刪除檔案
        
        mixer.init()
        mixer.music.load(f'{fp.name}.mp3')
        mixer.music.play()
        
speakChinese("洞3洞洞，伙房兵起床")