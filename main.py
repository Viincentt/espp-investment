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

DATEFORMAT = "%Y-%m-%d"
TICKER = "ticker"
DATES = "dates"
DOWNLOAD = "download"
MONTH = "month"
DAY = "day"
ADJCLOSE = "Adj Close"


def plotIt(companyName, df, color):
    ax = df[ADJCLOSE].plot(c=color, label=companyName)
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc="best")


def stats(l):
    if len(l) < 2:
        # If series has less than 2 elements, return 0 as there's no increase
        print(f"{0:15}", end=" " * 4)
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
        f"{nbDaysBuy:2} {buyAt:3.2f} {nbDaysSell:2} {sellAt:3.2f}",
        end=" " * 4,
    )


def printHeader(company):
    print(company[TICKER] + ":", end=" ")

    for date in company[DATES]:
        print(f"{date[DAY]:>8}-{calendar.month_name[date[MONTH]]}", end=" ")
    print()


def getMask(mask, company, stock):
    printHeader(company)
    for year in range(2020, 2024):
        print(year, end=": ")
        for date in company[DATES]:
            esppDate = datetime(year, date[MONTH], date[DAY])
            curMask = (stock.index >= esppDate - timedelta(days=1)) & (
                stock.index <= esppDate + timedelta(days=60)
            )
            stats(stock.loc[curMask, ADJCLOSE])
            mask |= curMask
        print()
    print()
    return mask


def within2Months(company):
    today = datetime.now()
    two_months_ago = today - timedelta(days=60)
    two_months_from_now = today + timedelta(days=60)
    return any(
        two_months_ago
        <= datetime(today.year, date[MONTH], date[DAY])
        <= two_months_from_now
        or two_months_ago
        <= datetime(today.year + 1, date[MONTH], date[DAY])
        <= two_months_from_now
        for date in company[DATES]
    )


def needToDownload(company):
    return (
        DOWNLOAD not in company
        or datetime.strptime(company[DOWNLOAD], DATEFORMAT)
        < datetime.today() - timedelta(weeks=52)
        or any(
            datetime.today() - timedelta(weeks=9)
            < datetime(datetime.today().year, date[MONTH], date[DAY])
            < datetime.strptime(company[DOWNLOAD], DATEFORMAT)
            < datetime.today() - timedelta(days=1)
            < datetime.today()
            for date in company[DATES]
        )
    )


def main():
    dataFilename = "data.json"
    with open(dataFilename) as file:
        companies = json.load(file)
    numberCompanies = len(companies)
    colors = iter(cm.rainbow(np.linspace(0, 1, numberCompanies)))
    for _name in companies:
        color = next(colors)
        company = companies[_name]
        csvName = "prices/" + company[TICKER] + ".csv"
        if needToDownload(company):
            data = yf.download(company[TICKER])
            today = datetime.today().strftime(DATEFORMAT)
            companies[_name][DOWNLOAD] = today
            with open(dataFilename, "w") as file:
                json.dump(companies, file, indent=2)
            data.to_csv(csvName)

        # only plot/analyze if the company has an espp date within 2 months in the past or future
        if within2Months(company):
            stock = pd.read_csv(csvName, index_col=0, parse_dates=True)
            # build mask + show stats
            mask = getMask(pd.Series(False, index=stock.index), company, stock)
            # plotIt ( maybe )
            stock.loc[~mask, ADJCLOSE] = None
            plotIt(company[TICKER], stock, color)

    print("buy after n days with -x% and sell after m days with +y%.")
    plt.show()


if __name__ == "__main__":
    main()
