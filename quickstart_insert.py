from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


try : 
    import argparse
    flags = argparse.ArgumentParser (parents=[tools.argparser]).parse_args()
except ImportError :
    flags = None

def calendar_message (start_time,end_time,summary) :

    EVENT = {

        'summary' :  summary,
        'start'   :  {'dateTime' : start_time},
        'end'     :  {'dateTime' : end_time}
    }

    e = CAL.events().insert(calendarId = 'primary',
        sendNotifications = True, body=EVENT).execute()

    print(''' *** %s event added: 
    Start : %s 
    End   : %s ''' % (e['summary'],
    e['start']['dateTime'], e['end']['dateTime'] ))
    


SCOPES = 'https://www.googleapis.com/auth/calendar'
store  = file.Storage('storage.json')
creds = store.get()

if not creds or creds.invalid : 
    flow  = client.flow_from_clientsecrets('assistant.json' , SCOPES)
    creds = tools.run_flow(flow, store, flags) \
            if flags else tools.run(flow,store)

CAL = build ('calendar', 'v3', http= creds.authorize(Http()))
gmt_off = '+08:50' 

summary ="춤추면 놀기."
start_date = '2019-02-07'
end_date = '2019-02-08T04:00:00Z'

print (end_date[0:-1]) 

start_time = start_date+'T04:01:00' + gmt_off
end_time   = end_date[0:-1] + gmt_off

calendar_message (start_time,end_time,summary)



