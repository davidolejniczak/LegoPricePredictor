import webbrowser
import PriceScraper
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Webserver for authentication
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser('/usr/bin/google-chrome')) 

# If modifying scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEETID")

if not SPREADSHEET_ID: 
  raise ValueError("No spreadsheet ID found in .env file.")

def authenticate(): 
  '''Authenticate with Google API'''
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
      creds = flow.run_local_server(port=0,open_browser=False)
      webbrowser.get('chrome').open('http://localhost:8080')
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    
  return creds

def updateValues():
  creds = authenticate()
  try:
    service = build("sheets", "v4", credentials=creds)
    values = PriceScraper.UpdatedLEGOData()
    data = [] 
    # Start = row in sheet
    for i, row_values in enumerate(values,start=5):
        range_name = f"LEGO!B{i}:E{i}"
        data.append({"range": range_name, "values": [row_values]})
    body = {"valueInputOption": "USER_ENTERED", "data": data}
    result = (
        service.spreadsheets()
        .values()
        .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
        .execute()
    )
    
    print(f"{(result.get('totalUpdatedCells'))} cells updated.")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error


def main():
  updateValues() 
    
if __name__ == "__main__":
  main()