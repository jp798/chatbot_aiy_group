import json 
import os
import requests  

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/webhook', methods =['POST'])    ##### WEBHOOK로 Dialogflow 대화 가지고 오기
def webhook() : 
    req = request.get_json(silent=True, force=True)
    print (json.dumps(req,indent=4))

    res = makeResponse(req)
    res = json.dumps(res,indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeResponse(req):          ##### 데이터 가공가히고 GET 날씨 정보 가져오기 
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("local-city")
   #date = parameters.get("date")
    print("######## "+city +"#################")

    #### GET 방식으로 날씨 정보 가져오기
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+city+'&units=imperial&appid=f6dacb03346d39ed9172cd49941688a3') 
    json_object = r.json()

    print ("#################################")
    print (json.dumps(json_object,indent=4)) # print 

    #### 날씨 정보 가공하기
    condition = json_object["weather"][0]["description"]  # 날씨 condition 
    temp = int(json_object["main"]["temp"]) -32 #섭씨 온도 변환 
    temp = int(temp*5/9)  #섭씨 온도 변환
    humidity  =  json_object["main"]["humidity"] # 현재 습도 변환 

    #### dialogflow에서 제공되는 답변입니다. ##########
    speech ="현재 " + city  + " 날씨는 " + condition + "입니다.  온도는 " + str(temp) +"C이며 습도는 " +str(humidity)+ "%입니다. " 
    return {
    "speech" : speech,
    "displayText" : speech,
    "source" : "apiai-weather-webhook"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT',5000)) 
    print("Starting app on port %d" % port)
    app.run(debug=True, port=port, host='0.0.0.0')

