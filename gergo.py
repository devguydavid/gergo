#!/usr/bin/env python

import os.path
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]


class TasklistNotFound(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(description="Add a task to a Google Tasklist")
    parser.add_argument("tasklist_name", help="Name of the tasklist (e.g., Inbox)")
    parser.add_argument("task_title", help="Title of the new task")
    parser.add_argument(
        "notes", nargs="?", default=None, help="Optional notes for the task"
    )
    args = parser.parse_args()

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("tasks", "v1", credentials=creds)

        # Find the tasklist ID for the provided tasklist name
        tasklists = service.tasklists().list().execute()
        inbox_id = None
        for tasklist in tasklists.get("items", []):
            if tasklist["title"] == args.tasklist_name:
                inbox_id = tasklist["id"]
                break

        if not inbox_id:
            raise TasklistNotFound(f"Tasklist '{args.tasklist_name}' not found.")

        # Create a new task in the tasklist
        task = {"title": args.task_title, "notes": args.notes}
        created_task = service.tasks().insert(tasklist=inbox_id, body=task).execute()
        print("Created task:", created_task["title"])
    except HttpError as err:
        print(err)
    except TasklistNotFound as err:
        print(f"{err} Please check the tasklist name and try again.")


if __name__ == "__main__":
    main()
