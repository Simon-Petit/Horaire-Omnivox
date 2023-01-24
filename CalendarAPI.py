from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from Scraper_Omnivox_HoraireV3 import scraper
from datetime import datetime

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
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time


def create_calendar():
    try:
        horaire_cegep_id = None
        page_token = None
        while True: 
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] == "Horaire Cégep":
                    horaire_cegep_id = calendar_list_entry['id']
                    break
            if horaire_cegep_id:
                break
            if 'nextPageToken' in calendar_list:
                page_token = calendar_list['nextPageToken']
            else:
                calendar_request_body = {
                    "summary": "Horaire Cégep",
                    "timeZone": "America/Montreal"
                }
                created_calendar = service.calendars().insert(body=calendar_request_body).execute()
                horaire_cegep_id = created_calendar['id']
                break
    except HttpError as error:
        print(f'An error occurred: {error}')
    return horaire_cegep_id

calendar_id = create_calendar()

def delete_all_events(date_début, date_fin):
    try:
        events_result = service.events().list(calendarId=calendar_id, timeMin=date_début, timeMax=date_fin, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
        for event in events:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')

events_list = scraper()

# create a dictionary to store the events grouped by day of the week
events_by_day = {}

# create a dictionary to store the events that will be added to the Google Calendar
calendar_events = {}

# iterate through each event in the events_list
for event_id, event in events_list.items():
    # convert the start and end times to datetime objects
    start_time = datetime.strptime(event['date_time_debut'].split("T")[1], '%H:%M:%S-05:00')
    end_time = datetime.strptime(event['date_time_fin'].split("T")[1], '%H:%M:%S-05:00')
    # get the day of the week from the start time
    day_of_week = datetime.strptime(event['date_time_debut'], '%Y-%m-%dT%H:%M:%S-05:00').strftime('%A')
    # if the day of the week already exists in the events_by_day dict
    if day_of_week in events_by_day:
        # flag to check if event already exists
        event_exists = False
        # iterate through each event in the current day
        for existing_event in events_by_day[day_of_week]:
            if event['titre'] == existing_event['titre'] and event['type_cours'] == existing_event['type_cours'] and event['local'] == existing_event['local'] and datetime.strptime(event['date_time_debut'].split("T")[1], '%H:%M:%S-05:00') == datetime.strptime(existing_event['date_time_debut'].split("T")[1], '%H:%M:%S-05:00') and datetime.strptime(event['date_time_fin'].split("T")[1], '%H:%M:%S-05:00') == datetime.strptime(existing_event['date_time_fin'].split("T")[1], '%H:%M:%S-05:00'):
                event_exists = True
            # check if the event already exists in the calendar_events dict
                if event['titre'] in calendar_events:
                    # check if the event has the same start and end time as the existing event in the calendar_events dict
                    if start_time == calendar_events[event['titre']]['start_time'] and end_time == calendar_events[event['titre']]['end_time']:
                        # the event already exists, do not add it to the calendar_events dict
                        break
                    else:
                        # the event has the same title but different start and end time, check other days in the other week
                        for day in events_by_day:
                            for existing_event in events_by_day[day]:
                                if event['titre'] == existing_event['titre'] and event['type_cours'] == existing_event['type_cours'] and event['local'] == existing_event['local']:
                                    start_time_existing = datetime.strptime(existing_event['date_time_debut'].split("T")[1], '%H:%M:%S-05:00')
                                    end_time_existing = datetime.strptime(existing_event['date_time_fin'].split("T")[1], '%H:%M:%S-05:00')
                                    if start_time == start_time_existing and end_time == end_time_existing:
                                        # the event already exists, do not add it to the calendar_events dict
                                        break
                                    else:
                                        # the event does not exist in the calendar_events dict, add it
                                        calendar_events[event['titre']] = {'start_time': start_time, 'end_time': end_time}
                else:
                    # the event does not exist in the calendar_events dict, add it
                    calendar_events[event['titre']] = {'start_time': start_time, 'end_time': end_time}
        if not event_exists:
            # if the event does not already exist in the current day, add it to the events_by_day dict
            events_by_day[day_of_week].append(event)
    else:
        # if the day of the week does not already exist in the events_by_day dict, add it
        events_by_day[day_of_week] = [event]


colorprofileID = int(input("Quelle couleurs voulez-vous que les évènements aillent?"))
if colorprofileID == 1:
    for cle in events_by_day:
        for event in events_by_day[cle]:
            if event['local'][:1] == "A":
                event["couleur"] = "5"
            elif event['local'][:1] == "B":
                event["couleur"] = "8"
            elif event['local'][:1] == "D":
                event["couleur"] = "3"
            elif event['local'][:1] == "E":
                event["couleur"] = "6"
            elif event['local'][:1] == "F":
                event["couleur"] = "7"
            elif event['local'][:1] == "G":
                event["couleur"] = "9"
            elif event['local'][:1] == "H":
                event["couleur"] = "2"
            elif event['local'][:1] == "J":
                event["couleur"] = "4"
            else:
                event["couleur"] = "8"
elif colorprofileID == 2:
    for cle in events_by_day:
        for event in events_by_day[cle]:
            event["couleur"] = "8"
            
FinHoraire = input("Entrez la date de fin de l'horaire (AAAAMMJJ):")

for cle in events_by_day:
    for event in events_by_day[cle]:        
        event_request_body = {
                "summary": event["titre"],
                "location": event["local"],
                'description': event["type_cours"],
                "start": {
                    "dateTime": event["date_time_debut"],
                    "timeZone": "America/Montreal",
                },
                "end": {
                    "dateTime": event["date_time_fin"],
                    "timeZone": "America/Montreal",
                },
                "recurrence": [
                    "RRULE:FREQ=WEEKLY;UNTIL={}".format(FinHoraire),
                ],
                "colorId": event["couleur"],
            }
            # Create the event
        service.events().insert(calendarId=calendar_id, body=event_request_body).execute()
        
date_début_relache = datetime.strptime(input("Entrez la date de début de la relâche (AAAAMMJJ):"), "%Y%m%d").isoformat() + "Z"
date_fin_relache = datetime.strptime(input("Entrez la date de fin de la relâche (AAAAMMJJ):"), "%Y%m%d").isoformat() + "Z"
""""
JourFerie = []
for i in range(0, int(input("Combien de jours fériés voulez-vous?"))):
    JourFerie.append(input("Veuillez entrer le jour férié (AAAAMMJJ):"))
for day in JourFerie:
    delete_all_events_of_a_specific_day(day)
"""
delete_all_events(date_début_relache, date_fin_relache)
delete_all_events("20230407", "20230411")
for event in events_by_day["Friday"]:        
    event_request_body = {
            "summary": event["titre"],
            "location": event["local"],
            'description': event["type_cours"],
            "start": {
                "dateTime": str(datetime.strptime(event['date_time_debut'], "%Y-%m-%dT%H:%M:%S-05:00").replace(day=11).replace(month=4).strftime("%Y-%m-%dT%H:%M:%S-05:00")),
                "timeZone": "America/Montreal",
            },
            "end": {
                "dateTime": str(datetime.strptime(event["date_time_fin"], "%Y-%m-%dT%H:%M:%S-05:00").replace(day=11).replace(month=4).strftime("%Y-%m-%dT%H:%M:%S-05:00")),
                "timeZone": "America/Montreal",
            },
            "colorId": event["couleur"],
        }
        # Create the event
    service.events().insert(calendarId=calendar_id, body=event_request_body).execute()