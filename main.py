import sys
import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
from dotenv import load_dotenv
from datetime import datetime

def check_envs(GOOGLE_AUTH):
    if not os.path.exists(GOOGLE_AUTH):
        print(f"Google File {GOOGLE_AUTH} not found. Abort")
        sys.exit()
    env_var_check = [ "STARLING_TOKEN" ]
    for var in env_var_check:
        if os.getenv(var) is None:
            print(f"Environment Variable {var} not set. Abort")
            sys.exit()
        else:
            print(f"{var} Loaded")
    # Load Environment Variables

def parse_timestamp(timestamp_string):
   return datetime.strptime(timestamp_string, "%Y-%m-%d")

def get_filtered_sheet_rows(sheet, timestamp_column_index):
    # Get all rows from the sheet
    all_rows = sheet.get_all_values()

    # Filter rows
    current_year = datetime.now().year
    current_month = datetime.now().month
    filtered_rows = []
    for row in all_rows[1:]:
        if row:  # Check if row is not empty
            timestamp = parse_timestamp(row[timestamp_column_index])
            if timestamp.year == current_year and timestamp.month == current_month:
                filtered_rows.append(row)
    return filtered_rows

def get_bank_filtered_transactions(response):
    # =============================
    # Set bank transactions to sync
    # =============================
    whitelist = ["Octopus Energy", "Thames Water", "Community Fibre", "Wandsworth Council" ]
    current_year = datetime.now().year
    current_month = datetime.now().month
    bank_filtered_transactions = []

    print("")
    try:
        for element in response.json()["mandates"]:
            if "lastDate" in element:
                timestamp = parse_timestamp(element["lastDate"])
                if element["originatorName"] in whitelist and timestamp.year == current_year and timestamp.month == current_month:
                    bank_filtered_transactions.append(element)
                    print(f"{element['lastDate']}-{element['originatorName']}: £{element['lastPayment']['lastAmount']['minorUnits'] / 100}")
    except:
        print(response.json())
    print("")
    return bank_filtered_transactions



# Define Starling Bank API endpoint
STARLING_BANK_API = 'https://api.starlingbank.com'

# Define Splitwise API endpoint
SPLITWISE_API = 'https://secure.splitwise.com/api/v3.0'

#Load env
load_dotenv()
# Local Execute
# GOOGLE_AUTH = os.getenv("GOOGLE_AUTH") # 
GOOGLE_AUTH = "token.json"
check_envs(GOOGLE_AUTH)
# Creds
STARLING_TOKEN = os.getenv("STARLING_TOKEN")


# Define headers for API requests
headers = {
   'Authorization': f'Bearer {STARLING_TOKEN}',
   'Accept': 'application/json',
}

# Fetch direct debits from Starling Bank
# response = requests.get(f'{STARLING_BANK_API}/api/v2/feed/account/{STARLING_ACCOUNT}/direct-debits', headers=headers)
response = requests.get(f'{STARLING_BANK_API}/api/v2/direct-debit/mandates', headers=headers)

bank_filtered_transactions = get_bank_filtered_transactions(response)

# Authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_AUTH, scope)
client = gspread.authorize(creds)

sheet = client.open('Digs Expensing').worksheet("5 Wimbledon Park Rd")

timestamp_column_index = 0
filtered_expensed_rows  = get_filtered_sheet_rows(sheet, timestamp_column_index)

print(f"Bank Debit Orders: {len(bank_filtered_transactions)} \nExpensed: {len(filtered_expensed_rows)} \n")
for bank_transaction in bank_filtered_transactions:
    exists = False
    for expensed_transaction in filtered_expensed_rows:
        if bank_transaction['originatorName'] == expensed_transaction[1]:
            exists = True
    if not exists:
        row = [bank_transaction['lastDate'], bank_transaction['originatorName'], bank_transaction['lastPayment']['lastAmount']['minorUnits'] / 100]
        print(f"Being appended {row}")
        sheet.append_row(row)


print("Script complete")