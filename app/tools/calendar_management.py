import os
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


from google.auth.exceptions import RefreshError

def get_calendar_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except RefreshError:
            creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(
                port=0,
                access_type="offline",
                prompt="consent"
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


def get_upcoming_events(max_results=10):
    service = get_calendar_service()

    now = dt.datetime.now(
        dt.timezone.utc
    ).isoformat()

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        )
        .execute()
    )

    return result.get("items", [])


def create_event(
    summary,
    start_datetime,
    end_datetime,
    description="",
    location=""
):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description,
        "location": location,
        "start": {
            "dateTime": start_datetime,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "Asia/Kolkata"
        }
    }

    created_event = (
        service.events()
        .insert(
            calendarId="primary",
            body=event
        )
        .execute()
    )

    return {
        "id": created_event["id"],
        "link": created_event.get("htmlLink")
    }


def update_event(event_name, changes: dict):
    service = get_calendar_service()

    matches = find_events(event_name)

    if not matches:
        raise ValueError(f"No event found with name '{event_name}'")

    event_id = matches[0]["id"]

    event = (
        service.events()
        .get(
            calendarId="primary",
            eventId=event_id
        )
        .execute()
    )

    field_mapping = {
        "summary": "summary",
        "description": "description",
        "location": "location"
    }

    for key, value in changes.items():
        if key in field_mapping:
            event[field_mapping[key]] = value

    if "start_datetime" in changes:
        event["start"] = {
            "dateTime": changes["start_datetime"],
            "timeZone": "Asia/Kolkata"
        }

    if "end_datetime" in changes:
        event["end"] = {
            "dateTime": changes["end_datetime"],
            "timeZone": "Asia/Kolkata"
        }

    updated_event = (
        service.events()
        .update(
            calendarId="primary",
            eventId=event_id,
            body=event
        )
        .execute()
    )

    return {
        "id": updated_event["id"],
        "summary": updated_event.get("summary")
    }


def delete_event(event_name):
    event_id = find_events(event_name)[0]["id"]
    service = get_calendar_service()

    (
        service.events()
        .delete(
            calendarId="primary",
            eventId=event_id
        )
        .execute()
    )

    return True


def find_events(query):
    service = get_calendar_service()

    events = (
        service.events()
        .list(
            calendarId="primary",
            q=query,
            singleEvents=True
        )
        .execute()
        .get("items", [])
    )

    return [
        {
            "id": event["id"],
            "summary": event.get("summary", "No Title")
        }
        for event in events
    ]


def return_upcoming_events():
    events = get_upcoming_events()

    if not events:
        print("No upcoming events found.")
        return

    print("\nUpcoming Events:\n")

    for event in events:
        start = event["start"].get(
            "dateTime",
            event["start"].get("date")
        )

        return f"{start} - {event.get('summary', 'No Title')}"


if __name__ == "__main__":
    try:

        # --------------------
        # CREATE EVENT EXAMPLE
        # --------------------
        # event = create_event(
        #     summary="AI Meeting",
        #     start_datetime="2026-06-05T15:00:00",
        #     end_datetime="2026-06-05T16:00:00",
        #     description="Testing Calendar API"
        # )
        # #
        # print(event)

        # --------------------
        # SEARCH EVENT EXAMPLE
        # --------------------
        print(find_events("AI Meeting"))

        # --------------------
        # UPDATE EVENT EXAMPLE
        # --------------------
        # update_event(
        #     event_id="4aj215lqsdduiqpsr09tmdfaf8",
        #     summary="Updated AI Meeting"
        # )

        # print_upcoming_events()

        # --------------------
        # DELETE EVENT EXAMPLE
        # --------------------
        # delete_event("4aj215lqsdduiqpsr09tmdfaf8")

    except HttpError as error:
        print("An error occurred:")
        print(error)
        