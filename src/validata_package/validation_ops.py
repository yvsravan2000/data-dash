# Import packages and modules | External
import os
import hashlib
import datetime
import pandas as pd
import streamlit as st

# Import packages and modules | Internal
from validata_package import config as cfg

# Function returns current datetime as string data type
def getCurrentDateTimeAsString() -> str:
    return '{date:%Y%m%d_%H%M%S}'.format(date=datetime.datetime.now())

# Function return current day, date & time as string data type
def getCurrentDayDateTimeAsString() -> str:
    return '{date:%A, %B %d, %Y, %I:%M:%S %p}'.format(date=datetime.datetime.now())

# Function to write data into a "csv" from dataframe
def writeDataFrameToCSV(dataframe, fpath) -> bool:
    try:
        dataframe.to_csv(fpath, index=False)
        return True
    except Exception as error:
        st.write(error)
        return False

# Function to write data into a "csv" from dataframe
def readDataFrameFromCSV(fpath) -> pd.DataFrame:
    try:
        dataframe = pd.read_csv(fpath)
        return dataframe
    except Exception as error:
        st.write(error)
        return pd.DataFrame()

# Function to write data into a "xlsx" from dataframe
def writeDataFrameToExcel(dataframe, fpath) -> bool:
    try:
        dataframe.to_excel(fpath, index=False)
        return True
    except Exception as error:
        st.write(error)
        return False

# Function to write data into a "xlsx" from dataframe
def readDataFrameFromExcel(fpath) -> pd.DataFrame:
    try:
        dataframe = pd.read_excel(fpath)
        return dataframe
    except Exception as error:
        st.write(error)
        return pd.DataFrame()

# Function returns the file names list
def getFileNamesList(username: str, directory: str) -> list:
    # Fetch all file names
    all_files = os.listdir(directory)

    # Filter out the files list based on the username
    if(username == "VEN00375@TJX.COM"):
        return all_files
    filtered_files_list = [file for file in all_files if file.startswith(username)]

    return filtered_files_list

# Function returns the hash value of dataframe
def getDataFrameHash(dataframe: pd.DataFrame):
    return hashlib.sha256(pd.util.hash_pandas_object(dataframe, index=True).values).hexdigest()

# Function to compare data between two dataframes
def compareDataFrames(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame, key_columns: list = []) -> pd.DataFrame:
    # Merge DataFrames to compare the data
    if(key_columns == []):
        validation_result_df = pd.merge(dataframe1, dataframe2, how='outer', on=None, indicator=True, suffixes=('_source', '_target'))
    else:
        validation_result_df = pd.merge(dataframe1, dataframe2, how='outer', on=key_columns, indicator=True, suffixes=('_source', '_target'))
    
    # Return results
    return validation_result_df

# Function to read file contents
def readFile(file) -> str:
    with open(file,'r', encoding='utf-8') as file:
        fileContent = file.read()
    return fileContent

# Function to write contents to file
def writeFile(str, file) -> None:
    with open(file, 'w', encoding='utf-8') as file:
        file.write(str)