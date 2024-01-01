import requests
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def check_envs(google_token):
    if not os.path.exists(google_token):
        raise FileNotFoundError(f"Google File {google_token} not found. Abort")
    load_dotenv()
    env_var_check = ["STARLING_TOKEN"]
    for var in env_var_check:
        if os.getenv(var) is None:
            raise ValueError(f"Environment Variable {var} not set. Abort")
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

def get_bank_filtered_transactions(whitelist):
    current_year = datetime.now().year
    current_month = datetime.now().month
    bank_filtered_transactions = []
    for element in response.json()["mandates"]:
        if "lastDate" in element:
            timestamp = parse_timestamp(element["lastDate"])
            if element["originatorName"] in whitelist and timestamp.year == current_year and timestamp.month == current_month:
                bank_filtered_transactions.append(element)
                print(element)
                print("")
    return bank_filtered_transactions

# Company Whitelist
whitelist = ["Community Fibre", "Octopus Energy", "Thames Water"]

# Define Starling Bank API endpoint
STARLING_BANK_API = 'https://api.starlingbank.com'

# Define Splitwise API endpoint
SPLITWISE_API = 'https://secure.splitwise.com/api/v3.0'

# Creds
STARLING_TOKEN = "eyJhbGciOiJQUzI1NiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAA_2WQS27kMAxEr9LwOgz80cfyLrtcYA5Ak1SPEFsyLHUwQZC7R4Y7mCDZkUXWU1HvTci5mRrcwmMuuC8hXmeML4-U1uahybe5DhXbfrDGgzU4ghLdgxu0QE9GiHtm79u6LP-2ZlKjdl3rtO4emoClmTrbDmrQ7hCQKN1ieU4Ly_4n8MEWxa3yCKY3FlRvBdD2MwxOkxm70XqNlV3Si8TTMSiyTs0e0CsEZdoWZm89aO1HR2zVaKU66kVPRJLzf5cZ0cDsWIEaTK3qXdBq6pQbnGmdOg6mtEld3_BNBMqOMSOVkOK0C_Il42v9oAzXhMuprFKQseAkHMol01_h2yIMFbBKLL9tJ9TLfo7qHiyJvnCUog_7iseTkDz4W-R8hxQscjBhY_9Tovx6Sr8irxhrPvmRlmpb5JI3pPtoxgXjV1PBkWtkSDt_SyryrYSw4vUu7EIStnImbT4-AbZXkCNWAgAA.hYHj5CUPjqYJh7IZgzT4aXvZO6DKyrg_82hkK6gJeBVhFQJZZX8PIQqnsPvFIOTz4xMuMQ5Y4KeVrppgICAzUGVA3zCnNuQacGnZLBd-i1RuMJSattgnQU4jR6P74JhMiG8zi8tQTOfL4JQVxnik5ZBNI0WQx44JHVwAQ0pRY67LTtMGbDldK1yFK-dlf0hxGEc9JiVypd0GvRDISlehQ3_OtiR_5VCVAVBvdlmepNhVEKcGn4VLP5jTCLAGt84wSyLD3aOGs_zRD_K8o383du2GuXUtpkjwgsYxI_dVwWI2MV_VbePEkjEaDmYoD61djkFRlf3dO66zzE7xN4QveC9LvYt_uSvlcpBK0i6qilAq1X-08GrcJMqMhYFZZZp1KUDPLMU9gLxEDGSonQgt-lnu01hLZgId_TjELLwIvxtwUVpcQqffp5PZJ2s8z5bFSc8dMjTujFl8gQxeu2Al84QZ07FJWPyZpq9gIoiH6vyUzTVU_JrsZa0Ruif1icCdD-tF6bPFvS729GWxNsztgZHUgoMus4t78HkSTUF3DC8br69JCh2OQHLRhaJN2tCOsV-aOTlQNDYQfP0-q00PluGCT7pRuUsycaaxrASmxAJS03OUxylXXpkw9sPSaAqHgd-8jTbd26yiLPS9oOxJ78H12IeZRMQlOra1ceuOLgc"

# Define headers for API requests
headers = {
   'Authorization': f'Bearer {STARLING_TOKEN}',
   'Accept': 'application/json',
}

# Fetch direct debits from Starling Bank
# response = requests.get(f'{STARLING_BANK_API}/api/v2/feed/account/{STARLING_ACCOUNT}/direct-debits', headers=headers)
response = requests.get(f'{STARLING_BANK_API}/api/v2/direct-debit/mandates', headers=headers)

one_month_ago = datetime.now() - timedelta(days=30)


bank_filtered_transactions = get_bank_filtered_transactions(whitelist)

# input("--------")
# Authenticaiton
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

google_token = "token.json"
check_envs(google_token)
creds = ServiceAccountCredentials.from_json_keyfile_name(google_token, scope)
client = gspread.authorize(creds)

sheet = client.open('Digs Expensing').worksheet("5 Wimbledon Park Rd")

timestamp_column_index = 0
filtered_expensed_rows  = get_filtered_sheet_rows(sheet, timestamp_column_index)

print(f"Filtered Debit Orders from bank ank_filtered_transactions: {len(bank_filtered_transactions)} \nfiltered_expensed_rows: {len(filtered_expensed_rows)}")
for bank_transaction in bank_filtered_transactions:
    exists = False
    for expensed_transaction in filtered_expensed_rows:
        if bank_transaction['originatorName'] == expensed_transaction[1]:
            exists = True
    if not exists:
        row = [bank_transaction['lastDate'], bank_transaction['originatorName'], bank_transaction['lastPayment']['lastAmount']['minorUnits'] / 100]
        print(f"Being appended {row}")
        # sheet.append_row(row)


print("Script complete")