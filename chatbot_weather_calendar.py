
#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging

from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient

from google.cloud import texttospeech
from pygame import mixer

import time

# -*- encoding: utf-8 -*-
import requests
import os
import json

from flask import Flask, request, jsonify,redirect

#from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


#databse  mysql 
import pymysql.cursors

#Configure db 
conn = pymysql.connect(host='127.0.0.1',user='pi',password='1234',charset='utf8mb4')


client = texttospeech.TextToSpeechClient()

try : 
    import argparse
    flags = argparse.ArgumentParser (parents=[tools.argparser]).parse_args()
except ImportError :
    flags = None


SCOPES = 'https://www.googleapis.com/auth/calendar'
store  = file.Storage('storage.json')
creds = store.get()

if not creds or creds.invalid : 
    flow  = client.flow_from_clientsecrets('assistant.json' , SCOPES)
    creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow,store)

CAL = build ('calendar', 'v3', http= creds.authorize(Http()))



def calendar(date,summary):


    start_date = date
    end_date   = date 
 


    gmt_off = '+00:00' 

    #start_date = '2019-02-07T04:00:00Z'
    #end_date = '2019-02-10T04:00:00Z'

    EVENT = {

        'summary' :  summary,
        'start'   :  {'dateTime' : start_date[0:-1] + gmt_off},
        'end'     :  {'dateTime' : end_date[0:-1] + gmt_off}
    }

    e = CAL.events().insert(calendarId = 'primary',
        sendNotifications = True, body=EVENT).execute()

    print (json.dumps(e,indent=4)) 

    print(''' *** %s event added: 
    Start : %s 
    End   : %s ''' % (e['summary'],
    e['start']['dateTime'], e['end']['dateTime'] ))
    
   
    speech = start_date +' 에서 ' + end_date +" 까지 " + summary + '(로) 예약되었습니다.'   
    
    return speech 




def get_answer(text, user_key):

    print("get_answer... start")
    data_send = { 
        'query': text,
        'sessionId': user_key,
        'lang': 'en',
    }
    data_header = {
        #'Authorization': 'Bearer 446d481d35154b9a9fda5913b8a15591',
        'Authorization': 'Bearer 8c4eb9f0dd714313b38a20bbf1557a99 ',
        'Content-Type': 'application/json; charset=utf-8'
    }
    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'
    data = res.json()   

    #data = receive.get_json(silent=True,force=True)
    print (json.dumps(data,indent=4))
    action = data['result']['action'] 


    ####  서울 날씨를 알려줌 ###########
    if action == "weather" :
       answer = "I heard wrong,Say it." 
       city = data['result']["parameters"]["local-city"]

       if city :
          r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=imperial&appid=f6dacb03346d39ed9172cd49941688a3')
          json_object = r.json()
          print (json.dumps(data,indent=4))

          condition = json_object["weather"][0]["description"]  # 날씨 condition 
          temp = int(json_object["main"]["temp"])-32 #섭씨 온도 변환 
          humidity  =  json_object["main"]["humidity"] # 현재 습도 변환 

          answer ="now "+ city  + "is " + condition + ".  온도는 " + str(temp) +"C이며 습도는 " +str(humidity)+ "%입니다. " 
          print ("날씨는:" + answer)

    elif action == "calendar" : 
          answer =  calendar(data['result']["parameters"]["date-time"],
                             data['result']["parameters"]["summary"])
   
    else :
       answer = data['result']['fulfillment']['speech']


    return answer

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['POST', 'GET'])
def webhook():

    content = request.args.get('content')
    userid = request.args.get('userid')

    return get_answer(content, userid)





def tts_answer(answer):

    # Set the text input to be synthesize
    synthesis_input = texttospeech.types.SynthesisInput(text = answer)
    count = len(str(synthesis_input))/60 ### 시간 딜레이 
    print ("count" + str(count))


    voice = texttospeech.types.VoiceSelectionParams(
            language_code='ko-KR',   ### ko-KR
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open('output.mp3', 'wb') as out:
    # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

    #os.system("omxplayer -o alsa output.mp3")
    mixer.init()
    mixer.music.load('output.mp3')
    mixer.music.play(0)
    time.sleep(count)

    print ("SOUND GOOD~~")


def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    
    
    with Board() as board:
        tts_answer("지금부터 말해 주세요. ")
        while True:

            try:
                with conn.cursor() as cursor:

                    cursor.execute("SELECT * FROM aiy.chat ORDER BY id DESC LIMIT 16;")
                    result = cursor.fetchall()

                    for row in result :
                      print(row)

            except :
               print ("error")

            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None :
                tts_answer('You are not say anything...". ㅠㅠㅠㅠ ')
                print('Sorry, I did not hear you.')

            else :
            ###  질문에 대한 출력 및 DB 저장 	
                print("나:"+ text)

                try:
                    with conn.cursor() as cursor:

                        sql = 'INSERT INTO aiy.chat(content) VALUES(%s)'
                        cursor.execute(sql,("나:"+text))
                        conn.commit()
                        #print("save:"+cursor.lastrowid+"열저장했습니다.")

                except:
                    print("DB1 에러")
            #conn.close()

            #### 답변에 대한 출력 
            
                text = get_answer(text,'jp')
                print('챗봇:"', text, '"')
            

                try:
                    with conn.cursor() as cursor:

                        sql = 'INSERT INTO aiy.chat(content) VALUES(%s)'
                        cursor.execute(sql,("챗봇:"+text))
                        conn.commit()
                    #print("save:"+cursor.lastrowid+"열저장했습니다.")

                except:
                    print("DB1 에러")

                tts_answer(text)


if __name__ == '__main__':
    main()
