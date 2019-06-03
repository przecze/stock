#!/usr/bin/env python3
import urllib.request
import os
from util import *
def createUrl(company_code: str):
    return "https://stooq.pl/q/d/l/?s={}&d1=20050101&d2=20100101&i=d".format(company_code)

def processList(listFileName: str):
    os.makedirs(os.path.join(os.getcwd(), RESOURCES_DIR), exist_ok=True)
    with open(listFileName) as f:
        for line in f:
            company_code = line.rstrip('\n').split(" ")[2].lower()
            resource_path = os.path.join(os.getcwd(), RESOURCES_DIR, company_code + RESOURCE_EXT)
            url = createUrl(company_code)
            print("downloading: "+url+" to "+resource_path)
            urllib.request.urlretrieve(url, resource_path)

processList("gpw_2007_list.txt")
