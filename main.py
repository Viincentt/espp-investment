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
from argparse import ArgumentParser

"""
        "Arista": { 
            ticker: "ANET", 
            "dates": [
                {month: 2, day: 15},
                {month: 8, day: 15}
            ]
        }
        "":{
            "ticker":"",
            "dates":[
            {"month":1, "day":1},
            {"month":1, "day":1}
            ]
        },
"""

DATEFORMAT = "%Y-%m-%d"
TICKER = "ticker"
DATES = "dates"
DOWNLOAD = "download"
MONTH = "month"
DAY = "day"
CLOSE = "Close"

parser = ArgumentParser()
parser.add_argument(
    "-w",
    "--window",
    type=int,
    default=60,
    required=False,
    metavar="N",
    help="Window size N in days to analyze after each ESPP date. Default: 60",
)
parser.add_argument(
    "-t",
    "--ticker",
    dest="tickers",
    type=str,
    required=False,
    metavar="TICKER",
    action="append",
    help="Company ticker to analyze.",
)
optionArgs = parser.parse_args()


def plotIt(companyName, df, color):
    ax = df[CLOSE].plot(c=color, label=companyName)
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc="best")


def stats(l):
    if len(l) < 2:
        # If series has less than 2 elements, return 0 as there's no increase
        return 0, 0, 0, 0, 0, 0

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

    # max loss
    maxDecrease, maxValue = 0, l.iloc[lowValueIdx]
    for i in range(lowValueIdx + 1, highValueIdx):
        if l.iloc[i] > maxValue:
            maxValue = l.iloc[i]
        else:
            current_decrease = maxValue - l.iloc[i]
            maxDecrease = max(maxDecrease, current_decrease)
    buyAt = 1 - round(lowValue / l.iloc[0], 2)
    sellAt = round(maxIncrease / lowValue, 2)
    stopLoss = round(maxDecrease / maxValue, 2)
    nbDaysBuy = (l.index[lowValueIdx] - l.index[0]).days
    nbDaysSell = (l.index[highValueIdx] - l.index[lowValueIdx]).days
    return nbDaysBuy, buyAt, nbDaysSell, sellAt, stopLoss, maxDecrease


def printHeader(company):
    print(f"{company[TICKER]:>4}:", end=" ")
    for date in company[DATES]:
        print(
            f"{str(date[DAY]) + calendar.month_name[date[MONTH]][:3]:^27}", end="    "
        )
    print()


def getMask(company, stock, lookBack=6):
    printHeader(company)
    mask = pd.Series(False, index=stock.index)
    today = datetime.now()
    for year in range(today.year - lookBack, today.year):
        print(year, end=": ")
        for date in company[DATES]:
            esppDate = datetime(year, date[MONTH], date[DAY])
            # TODO fix window range
            curMask = (stock.index >= esppDate) & (
                stock.index <= esppDate + timedelta(days=optionArgs.window)
            )
            a, b, c, d, e, f = stats(stock.loc[curMask, CLOSE])
            print(f"{-b:4.0%}({a:2}) {d:3.0%}({c:2}) {-e:4.0%}({f:4.2f})", end="    ")
            mask |= curMask
        print()
    print()
    return mask


def within(company, timeDuration):
    today = datetime.now()
    xTimeAgo = today - timedelta(days=5)  # TODO here
    xTimeFromNow = today + timeDuration
    return any(
        xTimeAgo <= datetime(today.year, date[MONTH], date[DAY]) <= xTimeFromNow
        # this to check if the date might not be next year
        or xTimeAgo <= datetime(today.year + 1, date[MONTH], date[DAY]) <= xTimeFromNow
        for date in company[DATES]
    )


def printHelper():
    print(
        "buy at -x%(after n days) and sell at +y%(after m days) and accept -z% loss(absolute value)."
    )


def main():
    dataFilename = "data.json"
    with open(dataFilename, "r") as file:
        companies = json.load(file)

    fromNow = timedelta(days=10)  # TODO here
    # TODO fix below NoneType
    if optionArgs.tickers != None:
        companies = {
            name: comp
            for name, comp in companies.items()
            if comp[TICKER] in map(str.upper, optionArgs.tickers)
        }
    else:
        companies = {
            name: comp for name, comp in companies.items() if within(comp, fromNow)
        }
    colors = iter(cm.rainbow(np.linspace(0, 1, len(companies))))

    # plot
    for name, company in companies.items():
        color = next(colors)
        # TODO period = ???
        stock = yf.Ticker(company[TICKER]).history(period="10y")
        stock.index = stock.index.tz_convert(None)
        # build mask + show stats
        mask = getMask(company, stock)
        # plotIt ( maybe )
        stock.loc[~mask, CLOSE] = None
        plotIt(company[TICKER], stock, color)

    printHelper()
    plt.show()


if __name__ == "__main__":
    main()
