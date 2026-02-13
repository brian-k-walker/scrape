import gspread
import google.auth

def init_gspread():
    # Automatically finds the credentials you just created in your terminal
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    return gspread.authorize(credentials)