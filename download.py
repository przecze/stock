#!/usr/bin/env python3
def createUrl(companyCode: str):
    return "https://stooq.pl/q/d/l/?s={}&d1=20050101&d2=20100101&i=d".format(companyCode.lower())

def processList(listFileName: str):
    with open(listFileName) as f:
        for line in f:
            print(createUrl(line.rstrip('\n').split(" ")[2]))
processList("gpw_2007_list.txt")
