
import pandas as pd
import numpy as np
import re
import streamlit as st



#import and clean data

def reviewclean(path: str):
    reviewdata = pd.read_csv("data.csv")
    return(reviewdata)

df = reviewclean("")
st.dataframe(df)
#create dataframe with just "ready for review" data

reviewdata = df.loc[:,"Application Signed?"]

