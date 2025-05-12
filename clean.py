import pandas as pd
import difflib
import numpy as np
import re
from datetime import date
import datetime
import os
import json
import sys
from github import Github

# Get the filename from the workflow

cwd = os.getcwd()
directory = f"{cwd}/Upload Here"
files = [file for file in os.listdir(directory) if file.endswith('.xlsx')]
path = files[0]
df = pd.read_excel(f"{directory}/{path}")


#standardize race values
possibler = ["Missing","African American","White","American Indian or Alaska Native","Hispanic","Asian","Decline to answer","Native Hawaiian or Other Pacific Islander",
             "Two or More"]
df['Race'] = df['Race'].astype(str)

df['Race'] = df['Race'].apply(lambda x: difflib.get_close_matches(x, possibler, n=1)[0] if difflib.get_close_matches(x, possibler, n=1) else x)
df["Race"] = df["Race"].astype(str)
df['Race'] = df['Race'].apply(lambda x: "Missing" if x == "nan"  else x)
df["Race"] = df["Race"].astype(str)

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
df['Pt State'] = df['Pt State'].apply(lambda x: x.upper())


#standardize city names
df["Pt City"] = df['Pt City'].apply(lambda x: x.capitalize() if type(x) == str else x)
df["Pt City"] = df['Pt City'].apply(lambda x: re.sub(r"[^a-zA-Z0-9\s]","",x) if type(x) == str else x)
df['Pt City'] = df['Pt City'].apply(lambda x: x.rstrip(" ") if type(x) == str else x)
df['Pt City'] = df['Pt City'].apply(lambda x: "Missing" if type(x) is float else x)

#standardize date time 
df['Payment Submitted?'] = df['Payment Submitted?'].apply(lambda x: x if type(x) is datetime.datetime else np.nan)
df["Grant Req Date"] =  pd.to_datetime(df["Grant Req Date"])
df["Grant Req Date"] = df['Grant Req Date'].apply(lambda x: x if type(x) is pd._libs.tslibs.timestamps.Timestamp else np.nan)
df["Time"] = df["Payment Submitted?"] - df["Grant Req Date"]
df["Time"] = df["Time"].apply(lambda x: x.days)
df["Year"] = df["Payment Submitted?"].apply(lambda x: x.year if type(x) is pd._libs.tslibs.timestamps.Timestamp else np.nan)
df["Year"].unique()

#standardize gender
df["Gender"] = df["Gender"].apply(lambda x: x if type(x) is str else "Missing")
#df['Gender'].apply(lambda x:"Missing" if type(x) is float else x)
df['Gender'] = df["Gender"].apply(lambda x: "Male" if type(re.match(r"(.+)?\s*\bmale\b\s*",x,re.IGNORECASE)) is re.Match else x)
df['Gender'] = df["Gender"].apply(lambda x: "Female" if type(re.match(r"(.+)?\s*female\s*(.+)?",x,re.IGNORECASE)) is re.Match  else x)

df['counter'] = 1


#Compute age
df["DOB"] = df["DOB"].astype(str)
df["DOB"] = df["DOB"].apply(lambda x: x[0:10])
for i,j in enumerate(df["DOB"]):
    if "2973" in j:
        df["DOB"][i] = np.nan
    elif "-" in j:
        df["DOB"][i] = pd.to_datetime(df["DOB"][i],format= "%Y-%m-%d")
    elif "/" in j:
        df["DOB"][i] = pd.to_datetime(df["DOB"][i],format= '%m/%d/%Y')
    else:
         df["DOB"][i] = np.nan
df["Age"] = df["DOB"].apply(lambda x: -(x.year - datetime.date.today().year) if type(x) != float else x)
df["Age"] = df["Age"].apply(lambda x: np.nan if x < 0 else x)

#convert household size to numeric
df['Household Size'] = df['Household Size'].apply(lambda x: np.nan if type(x) == str else x)
df['Household Size'] = df['Household Size'].fillna(-1)
df['Household Size'] = df['Household Size'].apply(lambda x: int(x) if x != -1 else np.nan)


#turn household income to numeric
df['Total Household Gross Monthly Income'] = df['Total Household Gross Monthly Income'].apply(lambda x: x if type(re.match(r'\d',str(x))) is re.Match else np.nan)


#standardize insurance type
fixspelling = ["Uninsured"]

df["Insurance Type"] = df['Insurance Type'].apply(lambda x: "Missing" if type(x) == float else x.capitalize())
df['Insurance Type'] = df['Insurance Type'].apply(lambda x: difflib.get_close_matches(x, fixspelling, n=1)[0] if difflib.get_close_matches(x, fixspelling, n=1) else x)
df['Insurance Type'] = df['Insurance Type'].apply(lambda x: "Medicare & medicaid" if x == "Medicaid & medicare" else x)

#standardize marital status
fixspelling = ["Separated"]
df["Marital Status"] = df['Marital Status'].apply(lambda x: "Missing" if type(x) == float else x.capitalize())
df["Marital Status"] = df['Marital Status'].apply(lambda x: difflib.get_close_matches(x, fixspelling, n=1)[0] if difflib.get_close_matches(x, fixspelling, n=1) else x)
df["Marital Status"] = df["Marital Status"].apply(lambda x: x.replace(" ","") if x != "Domestic partnership" else x)

#referral source tweaks
df['Referral Source'] = df['Referral Source'].apply(lambda x: "Missing" if type(x) is float else x)
df["Referral Source"] = df["Referral Source"].apply(lambda x:  x.rstrip())
df["Referral Source"] = df['Referral Source'].astype(str)



#amounts to numeric
df["Amount"] = df["Amount"].apply(lambda x: np.nan if type(x) == str else x)


#standardize types of assistance
df["Type of Assistance (CLASS)"] = df["Type of Assistance (CLASS)"].apply(lambda x: "Missing" if type(x) is float else x)
df["Type of Assistance (CLASS)"] = df["Type of Assistance (CLASS)"].apply(lambda x: x.capitalize())
df["Type of Assistance (CLASS)"] = df["Type of Assistance (CLASS)"].apply(lambda x: x.rstrip())

df["Type of Assistance (CLASS)"].unique()

#create household income variable
df["Monthly Household Income"] = df["Total Household Gross Monthly Income"]
df["Monthly Household Income"] = df["Monthly Household Income"].apply(lambda x: x if type(re.match(r"\d",str(x))) is re.Match else np.nan)
for i, j in enumerate(df["Monthly Household Income"]):
    print(j)
    if 2000 > j > 0:
        df.loc[i,"Monthly Household Income"] = "0-2000"
    elif 4000 > j > 2001:
        df.loc[i,"Monthly Household Income"] = "2001-4000"
    elif 6000 > j > 4001:
        df.loc[i,"Monthly Household Income"] = "4001-6000"
    elif 8000 > j >6001:
        df.loc[i,"Monthly Household Income"] = "6001-8000"  
    elif 10000 > j >8001:
        df.loc[i,"Monthly Household Income"] = "8001-10000"     
    elif j > 10000:
         df.loc[i,"Monthly Household Income"] = "10000+"  
    else:
        df.loc[i,"Monthly Household Income"] = "Missing"  


#Export
date = f'{datetime.date.today().month}-{datetime.date.today().year}'
df.to_csv(f"{cwd}/Clean Data/cleandata{date}.csv")

#g = Github("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")
#repo = g.get_user().get_repo("github.com/CasCraft1/Hope-Foundation-Project")

#with open(f"{cwd}/Clean Data/cleandata{date}.csv","rb") as file:
#    repo.create_file(f"{cwd}/Clean Data/cleandata{date}.csv","Script Upload",file.read(), branch = "main")
