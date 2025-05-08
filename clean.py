import pandas as pd
import difflib
import numpy as np
import re
from datetime import date

filepath = ""
df = pd.read_excel(filepath)


#standardize race values
possibler = ["Missing","African American","White","American Indian or Alaska Native","Hispanic","Asian","Decline to answer","Native Hawaiian or Other Pacific Islander",
             "Two or More"]
df['Race'] = df['Race'].astype(str)

df['Race'] = df['Race'].apply(lambda x: difflib.get_close_matches(x, possibler, n=1)[0] if difflib.get_close_matches(x, possibler, n=1) else x)
df['Race'].unique()

#standardize state names
# Define the dictionary
us_state_abbrev = {
    'ALABAMA': 'AL',
    'ALASKA': 'AK',
    'ARIZONA': 'AZ',
    'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA',
    'COLORADO': 'CO',
    'CONNECTICUT': 'CT',
    'DELAWARE': 'DE',
    'FLORIDA': 'FL',
    'GEORGIA': 'GA',
    'HAWAII': 'HI',
    'IDAHO': 'ID',
    'ILLINOIS': 'IL',
    'INDIANA': 'IN',
    'IOWA': 'IA',
    'KANSAS': 'KS',
    'KENTUCKY': 'KY',
    'LOUISIANA': 'LA',
    'MAINE': 'ME',
    'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA',
    'MICHIGAN': 'MI',
    'MINNESOTA': 'MN',
    'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO',
    'MONTANA': 'MT',
    'NEBRASKA': 'NE',
    'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH',
    'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM',
    'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC',
    'NORTH DAKOTA': 'ND',
    'OHIO': 'OH',
    'OKLAHOMA': 'OK',
    'OREGON': 'OR',
    'PENNSYLVANIA': 'PA',
    'RHODE ISLAND': 'RI',
    'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD',
    'TENNESSEE': 'TN',
    'TEXAS': 'TX',
    'UTAH': 'UT',
    'VERMONT': 'VT',
    'VIRGINIA': 'VA',
    'WASHINGTON': 'WA',
    'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI',
    'WYOMING': 'WY'
}
df['Pt State'] = df["Pt State"].apply(lambda x: x.upper() if type(x) == str else x)
df['Pt State'] = df["Pt State"].apply(lambda x: x.replace(" ", "") if type(x) == str else x)
df['Pt State'] = df['Pt State'].apply(lambda x: "Missing" if type(x) is float else x)
df['Pt State'] = df['Pt State'].apply(lambda x: us_state_abbrev[x] if (len(x) > 2) & ((x in us_state_abbrev) or (x in us_state_abbrev.values())) else x)
df['Pt State'].unique()


#standardize city names
df["Pt City"] = df['Pt City'].apply(lambda x: x.capitalize() if type(x) == str else x)
df["Pt City"] = df['Pt City'].apply(lambda x: re.sub(r"[^a-zA-Z0-9\s]","",x) if type(x) == str else x)
df['Pt City'] = df['Pt City'].apply(lambda x: x.rstrip(" ") if type(x) == str else x)
