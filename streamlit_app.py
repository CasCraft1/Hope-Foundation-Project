
import pandas as pd
import numpy as np
import re
import streamlit as st


#import and clean data

def reviewclean(path: str):
    reviewdata = pd.read_excel("C:/Econ 8320/my-python-project/UNO Service Learning Data Sheet De-Identified Version.xlsx")
    return(reviewdata)

df = reviewclean("C:/Econ 8320/my-python-project/UNO Service Learning Data Sheet De-Identified Version.xlsx")
st.dataframe(df)
#create dataframe with just "ready for review" data

reviewdata = df.loc[:,"Application Signed?"]
