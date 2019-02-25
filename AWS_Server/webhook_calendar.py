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

    res = makeResponse(req)
    res = json.dumps(res,indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeResponse(req):
    result = req.get("result")
    action = result.get("action")

    if action == "appointment"  :
         print("<<<<<<" + "appointment" + ">>>>>>>>")
 
    parameters = result.get("parameters")
    start_date = parameters.get("date-time")
    end_date = parameters.get("date-time") 
    summary = parameters.get("summary")
    #date = parameters.get("date")

    gmt_off = '+09:00' 

    
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
    
    return {
    "speech" : speech,
    "displayText" : speech,
    #"source" : "apiai-weather-webhook"
    }



if __name__ == '__main__':
    port = int(os.getenv('PORT',5000)) 
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

