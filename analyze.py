import loader
import networkx
import datetime
import pandas

HALF_A_YEAR = datetime.timedelta(days=365/2)
def calculateCorrelation(data):
    corr_df = data.corr(method='pearson')
    del corr_df.index.name
    return corr_df
def calculateDistances(data):
    return (2*(1-calculateCorrelation(data)))**(0.5)
def getNetwork(data):
    return networkx.convert_matrix.from_pandas_adjacency(calculateDistances(data))
def getTimeWindow(data, date):
    return data.loc[str((date-HALF_A_YEAR)):str((date+HALF_A_YEAR))]
def createNetworksSeries(data, start_date, end_date):
    networks = []
    br = pandas.bdate_range(start_date, end_date)
    for date in pandas.bdate_range(start_date, end_date, freq='w'):
        date = date.date() # remove wallclock time part
        print("Creating a network at :"+str(date))
        network = getNetwork(getTimeWindow(data, date))
        networks.append(pandas.Series([network], index = [date]))
    return pandas.concat(networks)
def createNetworksSeriesFull(data):
    dates = pandas.DatetimeIndex(data.index)
    return createNetworksSeries(data, (dates[0] + HALF_A_YEAR).date(), (dates[-1] - HALF_A_YEAR).date())
# creates the series only for the part of avaliable data. Useful for development if you want to test something fast
def createNetworksSeriesWithCount(data, count):
    dates = pandas.DatetimeIndex(data.index)
    return createNetworksSeries(data, (dates[0] + HALF_A_YEAR).date(), (dates[count] + HALF_A_YEAR).date())
