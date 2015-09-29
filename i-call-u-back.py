#

import bandwidth_sdk
import speech_recognition as GoogleTextToSpeechBefore
from dal import DAL,Field
import re


class GoogleTextToSpeech(object):
  def __init__(self,actual_api =GoogleTextToSpeechBefore):
    self.actual_api  =GoogleTextToSpeechBefore
    self.recognizer = self.actual_api.Recognizer()
  def transcribe(self,wav_file):
    #with open(wav_file) as WAV:
    source =  self.recognizer.WavFile(wav_file)
    audio =self.recognizer.record(source)
    try:
      return self.recognizer.recognize_google(audio)
    except Exception, e:
      return  e.__str__() 

  def translate(self,wav_file):
     return self.transcribe(wav_file)


class MySql(object):
  def __init__(self):
    self.settings =  Settings()
    self.connection = DAL("mysql://" +self.settings.mysql_user +":" +self.settings.mysql_pass  +"@" + self.settings.mysql_host +"/"+ self.settings.mysql_database)
    self.sample()
  def sample(self):
    self.connection.define("voicemail", 
           Field("text", "text")
           #Field("number")
     )
    self.connection.voicemail.insert(text="Hello this is an example I am calling from 15877784613 please return the call!") 
      

  def get_messages(self):
    return self.connection(getattr(self.connection,self.settings.mysql_table)).select()



class DataSource(object):
  def __init__(self, datasource=MySql):
    self.datasource =datasource()
  def  get_vm(self):
    return self.datasource.get_messages()

class VoiceRecognition(object):
  ##through a microservice
  ##consider sphinx or google voice
  def __init__(self, file='', provider=GoogleTextToSpeech):
    self.file = file
    self.provider = provider()
  def get_text(self):
    return  self.provider.translate(self.file)

class Settings(object):
  def __init__(self):
    self.settings =  json.loads(os.open("./settings.json","r"))
  def call_back_back(self):
    return self.settings['call_back'] 

## default init of bandwidth call API
class Bandwidth(object):
  def __init__(self,actual_api=bandwidth_sdk):
    self.settings = Settings() 
    self.actual_api =actual_api
    self.bwclient = bandwidth_sdk.Client(self.settings.bw_user_id,self.settings.bw_api_id,self.settings.bw_api_secret)
    self.from_number = self.settings.from_number
  def call_back(self, number):
    #self.bwclient.make_call(self.from_number, number)
    self.actual_api.Call(self.from_number,number)

  
class Caller(object):
  def __init__(self,provider=Bandwidth):
    self.provider =provider
  def call_back(self,number,do_what_after):
    self.provider.call(number)
    do_what_after(number) 

 


class Logger(object):
  def log(self,msg):
    open("./log", "a").write(msg)
      

class ProcessThings(object):
  def __init__(self):
    pass
  def run(self):
    self.datasource =  DataSource()
    self.translater =  VoiceRecognition()
    self.settings = Settings()
    vm  = self.datasource.get_vm()
    for i in vm:
      text = self.translater.get_text(i.text) 
      words =  text.split(" ")
      for j in words:
        if re.findall("\d{3}\-?(\d{3})\-?(\d{4})", j):
          if self.settings.call_back():
            ## demo we will just say we did it after
            Caller.call_back(j, lambda number: Logger().log("We called the number you needed" +  number) )



if __name__  ==  '__main__':
  ProcessThings().run()



