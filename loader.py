#!/usr/bin/env python3
import os
import pandas
from util import *
def loadDataFile(file_name: str):
    data = pandas.read_csv(file_name)
    data = data.rename(columns={RESOURCE_DATE_KEY:"Date", RESOURCE_CLOSE_KEY:"Close"})
    return data[["Date", "Close"]]
def loadAllAndClear(list_file_name: str):
    resources_dir = os.path.join(os.getcwd(), RESOURCES_DIR)
    with open(list_file_name) as f:
        data = []
        for line in f:
            company_code = line.rstrip('\n').split(" ")[2].lower()
            print(company_code)
            resource_path = os.path.join(resources_dir, company_code + RESOURCE_EXT)
            try:
                company_data = loadDataFile(resource_path)
            except FileNotFoundError:
                print("File not found:" + resource_path)
                continue
            except KeyError:
                print("Malformed data:" + resource_path)
                continue
            company_data['Symbol'] = company_code
            data.append(company_data)
        data = pandas.concat(data)
        data = data.pivot('Date', 'Symbol', 'Close').reset_index()
        print(data.head())
        for code in data.columns[1:]:# first column is "date"
            if data[code].isnull().iloc[0] or data[code].isnull().iloc[-1]:
                print("Removing data for index "+code+" because only part of the time window is avaliable")
                del data[code]
        data = data.dropna() # remove rows with nan's
        return data
data = loadAllAndClear("gpw_2007_list.txt")
