from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('assistant.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#    min_now = "2019-01-11"+"T04:06:55.7760922" 
    max_now = "2019-01-20"+"T22:06:55.776092Z" 
    print("now:" + now)
    print("insert event")


#    e = service.events().insert(calendarId='primary',
#                                sendNotifications = True, body = EVENT).execute() 

  


    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', 
                                        timeMin = max_now,
 #                                       timeMax= max_now,	
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

   
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))        
        print(start + ": " + event['summary'])



if __name__ == '__main__':
    main()
