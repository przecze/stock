#!/usr/bin/env python3
import urllib.request
import os
RESOURCES_DIR="resources"
RESOURCE_EXT=".csv"
def createUrl(companyCode: str):
    return "https://stooq.pl/q/d/l/?s={}&d1=20050101&d2=20100101&i=d".format(companyCode)

def processList(listFileName: str):
    os.makedirs(os.path.join(os.getcwd(), RESOURCES_DIR), exist_ok=True)
    with open(listFileName) as f:
        for line in f:
            companyCode = line.rstrip('\n').split(" ")[2].lower()
            resource_path = os.path.join(os.getcwd(), RESOURCES_DIR, companyCode + RESOURCE_EXT)
            url = createUrl(companyCode)
            print("downloading: "+url+" to "+resource_path)
            urllib.request.urlretrieve(url, resource_path)

processList("gpw_2007_list.txt")
