from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import datetime, csv, base64
import psycopg2



DAYS = 30
USER_ID = 'me'
CREDENTIALS = 'credentials.json'
COLUMNS = '(pageName, userName, facebookID, likesAtPosting, followerAtPosting, created, type, likes, comments, shares, love, wow, haha, sad, angry, care, videoShareStatus, postViews, totalViews, totalViewsForAllCrosspost, videoLength, url, message, link, finalLink, imageText, linkText, description, sponsorID, sponsorName, totalInteractions, overperformingScore)'
SUBJECT = 'Your Report is ready'
LOCALHOST = 'localhost'
TABLE = 'reportstable'
DB = 'DW-db'
USER = 'postgres'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']



def select_date():
    """create an epoch timestamp in order to take only monthly mails
        
    Returns:
        int: timestamp epoch from DAYS, in ms
    """
    now = datetime.datetime.now()
    then = now - datetime.timedelta(days=DAYS)
    
    return int(then.timestamp())*1000 # ms conversion

def logger_client():
    """Authentification and service delivery from gmail API
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens,
    # and is created automatically when the authorization flow
    # completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service

def call_listID(service):
    """listID is intended to be a list of email ID from the
     last month (or DAYS)

    Args:
        service: API query

    Returns:
        listID (list[int]): list of email IDs within DAYS
    """
    selectedDate = select_date()
    listID = []

    results = service.users().messages().list(
        userId=USER_ID
        ).execute()
    messages = results.get('messages', [])

    if not messages:
        raise SystemExit("Please check userId: {}".format(USER_ID))
    else:
        # loop is active until the DAYS timestamp is passed
        # API gives increasing dates only
        for message in messages:
            currentID = message['id']
            results2 = service.users().messages().get(
                userId=USER_ID,
                id=currentID,
                format='metadata' #  metadata is used to load less data
                ).execute()
            currentDate = results2['internalDate']
            # take only emails ID within DAYS
            if int(currentDate) > selectedDate:
                listID.append(currentID)
            else:
                break

    return listID

def call_IDFromSubject(service, subject, listID):
    """do a Subject-Filter from messages within DAYS and give back
    a dict {emailID: attachmentID}

    Args:
        service: API query
        subject (string): subject of mail
        listID (list[int]): list of email IDs within DAYS

    Returns:
        {emailID: attachmentID} matching with subject input
    """
    attachmentDict = {}

    for id in listID:
        results = service.users().messages().get(
            userId=USER_ID,
            id=id, format='full' # 'full' is needed for payload
            ).execute()
        payload = results.get('payload', [])
        nextID = False
        
        # checking if subject corresponds to our request
        headers = payload.get('headers', [])
        for header in headers:
            name = header.get('name')
            value = header.get('value')
            if name == 'Subject':
                if value != subject: # trigger break/continue for next id
                    nextID = True
                    break
        if nextID:
            continue

        # at this point we have the right id: we proceed with csv extraction
        parts = payload.get('parts')
        if not parts:
            raise SystemExit("No parts found. Please check ID: {}".format(id))
        else:
            for part in parts:
                mimeType = part.get('mimeType')
                if mimeType == 'text/csv':
                    body = part.get('body')
                    attachment = body.get('attachmentId')
                    attachmentDict[id] = attachment
        
    return attachmentDict


class HandlingAttachment:
    def __init__(self, service, emailID, attachmentID):
        self.emailID = emailID
        self.attachmentID = attachmentID
        self.results = service.users().messages().attachments().get(
            userId=USER_ID,
            messageId=emailID,
            id=attachmentID
            ).execute()
        self.dataBase64 = self.results['data']
        self.dataUFT8 = self._decode_data()

    def _decode_data(self): # internal method
        try:
            dataByte = base64.urlsafe_b64decode(self.dataBase64)
            dataUFT8 = dataByte.decode("utf-8")
            return dataUFT8
        except:
            raise SystemError("Please check the result from API")

    def create_temporary_file(self):
        # Do a temporary file (destroyed at end of computation)
        with open("{}.txt".format(self.emailID), 'w') as f:
            f.write(self.dataUFT8)

    def delete_temporary_file(self):
        # maybe we do not want to keep trace of data on local machine  
        os.remove("{}.txt".format(self.emailID))

    def arrange_data(self):
        # each value will be a query line in order to make a db-query for-loop
        with open("{}.txt".format(key), 'r') as f:
            data = [row for row in csv.reader(f.read().splitlines())]
            data.pop(0) # remove the header
            for row in data:
                for i in range(len(row)):
                    row[i] = row[i].replace("'","") # remove "'" for DB Query

        return data

    def send_to_db(self, row):
        conn = psycopg2.connect("host={} dbname={} user={}".format(
            LOCALHOST,
            DB,
            USER
            ))
        cur = conn.cursor()
        cur.execute('INSERT INTO {} {} VALUES {}'.format(
            TABLE,
            COLUMNS,
            tuple(row)))
        conn.commit()
    
        
if __name__ == '__main__':
    service = logger_client()
    listID = call_listID(service)
    attachmentDict = call_IDFromSubject(service, SUBJECT, listID)
    
    for key, value in attachmentDict.items():
        Attach = HandlingAttachment(service, key, value)
        Attach.create_temporary_file()
        data_to_send = Attach.arrange_data()
        for row in data_to_send:
            Attach.send_to_db(row)
        Attach.delete_temporary_file()
    print('TRANSFERT CSV Reports -> DB ** COMPLETE')
