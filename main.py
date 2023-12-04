import yfinance as yf
import json
import calendar

from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import pdb
import pandas as pd
import numpy as np

"""
        "Arista": { 
            ticker: "ANET", 
            "dates": [
                {month: 2, day: 15},
                {month: 8, day: 15}
            ]
        }
"""

ticker = "ticker"
dates = "dates"
download = "download"
month = "month"
day = "day"
adjClose = "Adj Close"


def plotIt(companyName, df, color):
    ax = df[adjClose].plot(c=color, label=companyName)
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc="best")


def max_increase(l):
    if len(l) < 2:
        # If series has less than 2 elements, return 0 as there's no increase
        print(f"{0:25.2f}", end="      ")
        return

    maxIncrease = 0
    minValue = l.iloc[0]
    lowValue, lowValueIdx, k, highValueIdx = 0, 0, 0, 0

    for i in range(1, len(l)):
        current_increase = l.iloc[i] - minValue
        if current_increase > maxIncrease:
            maxIncrease, highValueIdx = current_increase, i
            lowValue, lowValueIdx = minValue, k
        if l.iloc[i] < minValue:
            minValue = l.iloc[i]
            k = i
    buyAt = 1 - round(lowValue / l.iloc[0], 2)
    sellAt = round(maxIncrease / lowValue, 2)
    nbDaysBuy = (l.index[lowValueIdx] - l.index[0]).days
    nbDaysSell = (l.index[highValueIdx] - l.index[lowValueIdx]).days
    print(
        f"{nbDaysBuy:2} {buyAt:5.2f} {nbDaysSell:10} {sellAt:5.2f}",
        end="      ",
    )


def updateMask(mask, company, stock):
    print(company[ticker] + ":", end="  ")

    for date in company[dates]:
        print(f"{date[day]}-{calendar.month_name[date[month]]}", end=" " * 33)
    print()

    for year in range(2020, 2024):
        print(year, end=": ")
        for date in company[dates]:
            esppDate = datetime(year, date[month], date[day])
            tmpMask = (stock.index >= esppDate - timedelta(days=1)) & (
                stock.index <= esppDate + timedelta(days=60)
            )
            max_increase(stock.loc[tmpMask, adjClose])
            mask |= tmpMask
        print()
    print()

    return mask


def main():
    dataFilename = "data.json"
    with open(dataFilename) as file:
        companies = json.load(file)
    dateFormat = "%Y-%m-%d"
    numberCompanies = len(companies)
    colors = iter(cm.rainbow(np.linspace(0, 1, numberCompanies)))
    for _name in companies:
        color = next(colors)
        company = companies[_name]
        csvName = "prices/" + company[ticker] + ".csv"
        todo = 0
        if (
            download not in company
            or datetime.strptime(company[download], dateFormat)
            < datetime.today() - timedelta(weeks=52)
            or any(
                datetime.today() - timedelta(weeks=9)
                < datetime(datetime.today().year, date[month], date[day])
                < datetime.today()
                for date in company[dates]
            )
        ):
            data = yf.download(company[ticker])
            today = datetime.today().strftime(dateFormat)
            companies[_name][download] = today
            with open(dataFilename, "w") as file:
                json.dump(companies, file, indent=2)
            data.to_csv(csvName)
        stock = pd.read_csv(csvName, index_col=0, parse_dates=True)
        # getCorrectData
        # show stats
        # plotIt ( maybe )
        mask = pd.Series(False, index=stock.index)
        mask = updateMask(mask, company, stock)
        stock.loc[~mask, adjClose] = None
        plotIt(company[ticker], stock, color)
    print("buy after n days with -x% and sell after m days with +y%.")
    plt.show()


def tmp():
    # update company["dates"] to be a list
    """
    dates: {
    "month": []
    "day": []
    }
    """
    dataFilename = "data.json"
    with open(dataFilename) as file:
        companies = json.load(file)


if __name__ == "__main__":
    tmp()
    # main()
