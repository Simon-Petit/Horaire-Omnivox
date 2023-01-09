from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Scraper_Omnivox_HoraireV3 import scraper

info = scraper()

def colorprofile():
    colorprofileID = int(input("Quelle couleurs voulez-vous que les évènements aillent?"))
    if colorprofileID == 1:
        for cle in info.keys():
            if info[cle]["local"][:1] == "A":
                info[cle]["couleur"] = "5"
            elif info[cle]["local"][:1] == "B":
                info[cle]["couleur"] = "8"
            elif info[cle]["local"][:1] == "D":
                info[cle]["couleur"] = "3"
            elif info[cle]["local"][:1] == "E":
                info[cle]["couleur"] = "6"
            elif info[cle]["local"][:1] == "F":
                info[cle]["couleur"] = "7"
            elif info[cle]["local"][:1] == "G":
                info[cle]["couleur"] = "9"
            elif info[cle]["local"][:1] == "H":
                info[cle]["couleur"] = "2"
            elif info[cle]["local"][:1] == "J":
                info[cle]["couleur"] = "4"
            else:
                info[cle]["couleur"] = "8"
    elif colorprofileID == 2:
        for cle in info.keys():
           info[cle]["couleur"] = "8"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar',"https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/calendar.events.readonly"]


creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('calendar', 'v3', credentials=creds)
# Call the Calendar API
now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time


def create_calendar():
    try:
        calendar_list_summary = []
        page_token = None
        while True: 
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                calendar_list_summary.append(calendar_list_entry['summary'])
                calendar_list_summary.append(calendar_list_entry['id'])
            if 'Horaire Cégep' not in calendar_list_summary:
                calendar_request_body = {
                    "summary": "Horaire Cégep",
                    "description": "L'horaire de vos cours est précis pour les 10 prochains jours.",
                    "timeZone": "America/Montreal",
                    "colorId": "6" 
                }
                Calendrier = service.calendars().insert(body=calendar_request_body).execute()
                return Calendrier['id']
            else:
                return calendar_list_summary[3]            
            if not page_token:
                break
    except HttpError as error:
        print('An error occurred: %s' % error)  

def get_event_by_date(date):
    try:
        page_token = None
        while True:
            events = service.events().list(calendarId= create_calendar(), pageToken=page_token).execute()
            for event in events['items']:
                if event.get('start').get('dateTime') == date:
                    return (event['summary'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print('An error occurred: %s' % error)

def get_event_end(summary, date_début):
    try:
        page_token = None
        while True:
            events = service.events().list(calendarId= create_calendar(), pageToken=page_token).execute()
            for event in events['items']:
                if event.get('summary') == summary and event.get('start').get('dateTime') == date_début:
                    return (event['end'].get('dateTime'))
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print('An error occurred: %s' % error)


def delete_all_events(date_début, date_fin):
    try:
        page_token = None
        while True:
            events = service.events().list(calendarId= create_calendar(), pageToken=page_token).execute()
            for event in events['items']:
                if event.get('start').get('dateTime') >= date_début and event.get('end').get('dateTime') <= date_fin:
                    service.events().delete(calendarId= create_calendar(), eventId=event['id']).execute()
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except HttpError as error:
        print('An error occurred: %s' % error)
        
FinHoraire = input("Entrez la date de fin de l'horaire (AAAAMMJJ):")
def CreateEvent():
    for cle in info.keys():
        event = {
        'summary': info[cle]["titre"],
        'location': info[cle]["local"],
        'description': info[cle]["type_cours"],
        "colorId": info[cle]["couleur"],
        'start': {
        'dateTime': info[cle]["date_time_debut"],
        'timeZone': 'America/Montreal',
        },
        'end': {
        'dateTime': info[cle]["date_time_fin"],
        'timeZone': 'America/Montreal',
        },
        }
        
        if get_event_by_date(info[cle]["date_time_debut"]) != info[cle]["titre"] or get_event_end(info[cle]["titre"], info[cle]["date_time_debut"]) != info[cle]["date_time_fin"]:
            event = service.events().insert(calendarId= create_calendar(), body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

def CreateHoraireExam():
    for cle in info.keys():
        event = {
        'summary': info[cle]["titre"],
        'location': info[cle]["local"],
        'description': info[cle]["type_cours"],
        "colorId": info[cle]["couleur"],
        'start': {
        'dateTime': info[cle]["date_time_debut"],
        'timeZone': 'America/Montreal',
        },
        'end': {
        'dateTime': info[cle]["date_time_fin"],
        'timeZone': 'America/Montreal',
        },
        }
        
        if int(info[cle]["date_time_debut"][:10].replace("-","")) > int(FinHoraire) and get_event_by_date(info[cle]["date_time_debut"]) != info[cle]["titre"]:
            event = service.events().insert(calendarId= create_calendar(), body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

def CreateHorairecomplet():
    for cle in info.keys():
        event = {
        'summary': info[cle]["titre"],
        'location': info[cle]["local"],
        'description': info[cle]["type_cours"],
        "colorId": info[cle]["couleur"],
        'start': {
        'dateTime': info[cle]["date_time_debut"],
        'timeZone': 'America/Montreal',
        },
        'end': {
        'dateTime': info[cle]["date_time_fin"],
        'timeZone': 'America/Montreal',
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;UNTIL=%s" % FinHoraire,
            "EXDATE:%s; COUNT=2" % str(info[cle]["date_time_debut"][:10].replace("-",""))
            ],
        }
        
        if get_event_by_date(info[cle]["date_time_debut"]) != info[cle]["titre"] or get_event_end(info[cle]["titre"], info[cle]["date_time_debut"]) != info[cle]["date_time_fin"]:
            event = service.events().insert(calendarId= create_calendar(), body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    
    create_calendar()
    colorprofile()
    CreateEvent()
    CreateHorairecomplet()
    CreateHoraireExam()
    date_début_relache = input("Entrez la date de début de la relâche (AAAA-MM-JJ):")
    date_fin_relache = input("Entrez la date de fin de la relâche (AAAA-MM-JJ):")
    delete_all_events(date_début_relache, date_fin_relache)