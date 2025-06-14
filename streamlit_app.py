
import pandas as pd
import numpy as np
import re
import streamlit as st
import os
import plotly.express as pt
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)



#use first csv file within the working directory
cwd = os.getcwd()
files = [file for file in os.listdir(f"{cwd}/Clean Data/") if file.endswith('.csv')]
path = files[0]
data = pd.read_csv(f"{cwd}/Clean Data/{files[0]}")

st.set_page_config(layout="wide")

#side bar that reads in different sheets
sidebar = st.sidebar
with sidebar:
       selection =  st.radio(" Select File", files)
       data = pd.read_csv(f"{cwd}/Clean Data/{selection}")

#filter dataframe function from streamlit website
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters",key = "NOT DEFAULT")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter by", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


#import and clean data to see pending application characteristics
def reviewclean(data):
    df = data
    dfslim = df.loc[:,['Patient ID#',"Grant Req Date","App Year",'Request Status','Application Signed?']]
    dfslim = dfslim.loc[dfslim["Request Status"]=="Pending"]
    #fill in missing values 
    dfslim["Application Signed?"] = df["Application Signed?"].fillna("Not Specified")
    dfslim["Patient ID#"] = dfslim["Patient ID#"].astype(str)
    return(dfslim)

#call function for application related data
applicationdata = reviewclean(data)

#function to clean data for demographic review
def democlean(data):
    
    
    df = data
    df = df.dropna(subset=["Amount ($)"])
    df = df[df["Request Status"] == "Approved"]
    columnmap = {"State":"State", "City":"City","Race":"Race",
    "Gender":"Gender","Age":"Age","Marital Status":"Marital Status","Insurance Type":"Insurance Type","Household Size":"Household Size","Monthly Household Income":"Monthly Household Income"}
    columns = [columnmap[i] for i in columnmap]
    columns.append("Amount ($)")
    output = df[columns]
    return output

#call democlean with specified demographics

demodf = democlean(data)

#function to subset data for the time related outputs
def timeclean(data):
    metrics = data[['Patient ID#',"Year",'Grant Req Date','Payment Submitted?','Time']]
    finalmetrics = metrics[["Year", "Time"]]
    mean = finalmetrics.groupby("Year").mean()
    std = finalmetrics.groupby("Year").std()
    min = finalmetrics.groupby("Year").min()
    max = finalmetrics.groupby("Year").max()
    stats = [mean,std,min,max]
    finalstats = mean
    finalstats["Std. Dev"] = std.iloc[:,0]
    finalstats["Min"] = min.iloc[:,0]
    finalstats["Max"] = max.iloc[:,0]
    finalstats = finalstats.rename(columns={"Time":"Mean"})
    return [finalstats,finalmetrics]
#call function and small adjustments
timeoutput = timeclean(data)
timemetrics = timeoutput[0].fillna(0)
timemetrics = timemetrics[timemetrics["Mean"]>0]
timedata = timeoutput[1]
#function to subset data for remainder funds related outputs
def remfunds(data):
    columns = ["App Year",'Type of Assistance',"Count","Remaining Balance ($)","Request Status"]
    count = data.loc[:,columns]
    count["Remaining Balance ($)"] = count["Remaining Balance ($)"].apply(lambda x: np.nan if type(x) is str else x)
    count = count[count["Remaining Balance ($)"]>0]
    count = count[count["Request Status"] == "Approved"]
    count = count.drop("Request Status", axis = 1)
    output = count#.groupby(["App Year",'Type of Assistance']).sum()
      
    return output
#call function
remfundata = remfunds(data)
#function to subset data for metrics related outputs
def kmetric(data):
    columns = ["Year","Patient ID#","Request Status",'Type of Assistance',"Count", "Amount ($)"]
    df = data.loc[:,columns]
    df = df[df["Request Status"]== "Approved"]
    df["Year"] = df["Year"]
    return df

#call function
metricdata = kmetric(data)

#create tabs
reviewapps, demodata, timdata, remainderdata, kpidata, = st.tabs(["Applications for Review",
"Support by Demographics", "Assistance Process Time", "Leftover Funds", "Key Metrics"])

#create dataframe with just "ready for review" data
with reviewapps:
    st.text("Pending Requests")
    st.dataframe(filter_dataframe(applicationdata.copy().reset_index(drop = True)))


#create table that aggregates using sum based on demographic filters
with demodata:
    #create filters
    democol = st.columns([.3,.7])
    demographics = ["State","City","Race","Gender","Age", "Marital Status","Insurance Type","Household Size","Monthly Household Income"]
    #create buttons
    with democol[0]:
        boxes = list(map(lambda x: st.checkbox(x,key = x[-2:]),demographics))

        selected = []
        for i, j in enumerate(boxes):
            if j:
                selected.append((j,demographics[i]))
        
        appliedfilters = [i[1] for i in selected if i[0]==True]
        #apply filters to dataframe
        columnmap = {"State":"State", "City":"City","Race":"Race",
    "Gender":"Gender","Age":"Age","Marital Status":"Marital Status","Insurance Type":"Insurance Type","Household Size":"Household Size","Monthly Household Income":"Monthly Household Income"}
        columns = [columnmap[i] for i in appliedfilters]
        newdf = demodf[columns]
        newdf["Amount ($)"] = demodf["Amount ($)"]
        with democol[1]:
            if len(selected) >0:     
                st.dataframe(newdf.groupby(columns).sum())
            else:
                ""
        #chart related data clean and rendering
        chartdf = newdf
        if "Household Size" in chartdf.columns:
            chartdf["Household Size"] = chartdf["Household Size"].astype(str)
        if "Age" in chartdf.columns:
            chartdf["Age"] = chartdf["Age"].astype(str)
        #render chart
        with st.container( ):
            if len(selected)>0:
                st.plotly_chart(pt.sunburst(chartdf,path = columns, values = 'Amount ($)'),)

with timdata:
    st.text("Assistance Process Time Stats in Days")
    st.dataframe(timemetrics)
    yeardata = timedata
    years = yeardata["Year"].unique()
    #render chart based on most recent year
    plotdata = yeardata[yeardata["Year"]==years[-1]]
    timefig = pt.box(plotdata, y="Time")
    st.text(f"Process Time Distribution for {int(years[-1])}")
    st.plotly_chart(timefig)

with remainderdata:
    st.text("Total Assistance by Assistance Type")
    st.dataframe(remfundata.groupby(["App Year",'Type of Assistance']).sum())
    st.plotly_chart(pt.bar(remfundata, x="Type of Assistance", y = "Remaining Balance ($)", title = "Total Remaining Funds by Assistance Type"))
    avgtype = ["App Year",'Type of Assistance',"Remaining Balance ($)"]
    remfundata2 = remfundata.loc[:,["App Year",'Type of Assistance',"Remaining Balance ($)"]]
    st.text("Average Remaining Balance by Application Year  by Type")
    st.dataframe(remfundata2.groupby(["App Year",'Type of Assistance']).mean())
    remfundata2 = remfundata2.drop("App Year",axis = 1)
    st.plotly_chart(pt.bar(remfundata2.groupby(['Type of Assistance'],as_index = False).mean(),x = "Type of Assistance",y = "Remaining Balance ($)", title = "Average Remaining Balance by Type"))
    
with kpidata:
    kpifilter = st.checkbox("By Assistance Type")
    container1 = st.container()
    container2 = st.container()
    if kpifilter:
        groupings = ["Year", "Type of Assistance"]
        total = metricdata.loc[:,["Year","Type of Assistance","Amount ($)"]]
        count = metricdata.loc[:,["Patient ID#","Type of Assistance","Year","Count"]]
    else:
        groupings = ["Year"]
        total = metricdata.loc[:,["Year","Amount ($)"]]
        count = metricdata.loc[:,["Patient ID#","Year","Count"]]       
    count = count.drop_duplicates(subset = ["Patient ID#","Year"])
    count = count.drop("Patient ID#", axis =1)
    count = count.groupby(groupings, as_index = False).count()
    total = total.groupby(groupings, as_index = False).sum()
    with container1:
        kpicolumns1 = st.columns(2)
        with kpicolumns1[0]:
            if kpifilter:
                fig = pt.line(total,x = "Year", y = "Amount ($)", color = "Type of Assistance", title="Total Assistance by Year by Assistance Type")
                st.plotly_chart(fig )
            else:
                fig = pt.line(total,x = "Year", y = "Amount ($)", title= "Total Assistance by Year")
                st.plotly_chart(fig )               
        with kpicolumns1[1]:
            st.dataframe(total)
    with container2:
        kpicolumns2 = st.columns(2)
        with kpicolumns2[0]:
            if kpifilter:
                fig2 = pt.line(count,x= "Year",y = "Count", color = "Type of Assistance", title="Individuals Helped by Year by Assistance Type")
                st.plotly_chart(fig2)
            else:
                fig2 = pt.line(count,x= "Year",y = "Count",title="Individuals Helped by Year")
                st.plotly_chart(fig2)               
        with kpicolumns2[1]:
            st.dataframe(count)

