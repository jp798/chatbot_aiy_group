from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import json 
import os
import requests  

from flask import Flask
from flask import request
from flask import make_response


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




app = Flask(__name__)

@app.route('/webhook', methods =['POST'])
def webhook() : 
    req = request.get_json(silent=True, force=True)
    print ("##############################")
    print (json.dumps(req,indent=4))



    result = req.get("result")
    action = result.get("action")
    parameters = result.get("parameters") 

    if action == "calendar"  :     ### action 값으로 구분하기. calendar  예약하기 
         res = calendar(parameters.get("date-time"),parameters.get("summary"))

    elif  action =="weather"  :    ### action 값으로 구분하기. weather 날씨 
         res = weather(parameters.get("local-city"))

    else    :   #### 관련된 action 값이 없을 경우에 아래와 같이 적용
         res = {  "speech" : "죄송해요. 답변해 드릴수가 없네요." ,
               "displayText" : "죄송해요. 답변해 드릴수가 없네요.",
               "source" : "apiai-webhook"
                }    

    res = json.dumps(res,indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def calendar(date,summary):

    start_date = date
    end_date   = date
    gmt_off = '+09:00' 


    EVENT = {
        'summary' :  summary,
        'start'   :  {'dateTime' : start_date[0:-1] + gmt_off},  ### calendar 날짜 형식으로 parsing
        'end'     :  {'dateTime' : end_date[0:-1] + gmt_off}    ### calenar 날짜 형식으로 parsing 
    }

    e = CAL.events().insert(calendarId = 'primary',
        sendNotifications = True, body=EVENT).execute()  ### calendar 입력하기

    #### calendar 출력 하기 ############
    print ("#################################")
    print (json.dumps(e,indent=4)) 

    print(''' *** %s event added: 
    Start : %s 
    End   : %s ''' % (e['summary'],
    e['start']['dateTime'], e['end']['dateTime'] ))

    speech = start_date +' 에서 ' + end_date +" 까지 " + summary + '(로) 예약되었습니다.'   

    ##### calendar speech  메시지로 전달하기 #######  
    return {
    "speech" : speech,
    "displayText" : speech,
    "source" : "apiai-webhook"
    }


def weather(city) :


    #### GET 방식으로 날짜 정보 가져오기 ######
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=imperial&appid=f6dacb03346d39ed9172cd49941688a3')
    json_object = r.json() ###  Json 파일로 파싱하기 

    print ("#################################")
    print (json.dumps(json_object,indent=4))

    # http://api.openweathermap.org/data/2.5/weather?q=seoul&units=imperial&appid=f6dacb03346d39ed9172cd49941688a3
    # "weather":[{"id":721,"main":"Haze","description":"haze","icon":"50d"}],"base":"stations","main":{"temp":57.65,"pressure":1012,"humidity":67,"temp_min":55.4,"temp_max":59}



    ######  날짜정보를 가지고 오기... Json 형태로 파싱하여 보여주기 ###### 
    condition = json_object["weather"][0]["description"]
    temp = int(json_object["main"]["temp"]) -32
    humidity  =  json_object["main"]["humidity"]

    #####  문자열로 가지고 오기  
    speech ="현재 " + city  + " 날씨는 " + condition + "입니다.  온도는 " + str(temp) +"C이며 습도는 " +str(humidity)+ "%입니다. " 
    return {
    "speech" : speech,
    "displayText" : speech,
    "source" : "apiai-webhook"
    }




if __name__ == '__main__':
    port = int(os.getenv('PORT',5000)) 
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')

