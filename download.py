#!/usr/bin/env python3
import urllib.request
import os
from util import *
def createUrl(company_code: str):
    return "https://stooq.pl/q/d/l/?s={}&d1=20050101&d2=20100101&i=d".format(company_code)

def processList(listFileName: str, start: int):
    os.makedirs(os.path.join(os.getcwd(), RESOURCES_DIR), exist_ok=True)
    with open(listFileName) as f:
        for i in range(start):
            f.readline()
        for line in f:
            company_code = line.rstrip('\n').split(" ")[2].lower()
            resource_path = os.path.join(os.getcwd(), RESOURCES_DIR, company_code + RESOURCE_EXT)
            url = createUrl(company_code)
            print("downloading: "+url+" to "+resource_path)
            urllib.request.urlretrieve(url, resource_path)
            with open(resource_path) as resource_file:
                if "dzienny limit" in resource_file.readline():
                    print("stopping at line = "+ line)
                    return

processList("gpw_2007_list.txt", 95)
