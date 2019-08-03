import requests
import config

session = requests.Session()

def fetch():
    sid = config.GOOGLE_SPREADSHEET_ID
    key = config.GOOGLE_API_KEY

    url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/A:B"
    url = url.format(sid)

    params = {
        # 'majorDimension': 'COLUMNS',
        'key': key
    }
    r = session.get(url, params=params)
    data = r.json()
    return data['values']

