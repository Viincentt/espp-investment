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
ADJCLOSE = "Adj Close"


def plotIt(companyName, df, color):
    ax = df[ADJCLOSE].plot(c=color, label=companyName)
    lines, labels = ax.get_legend_handles_labels()
    ax.legend(lines, labels, loc="best")


def stats(l):
    if len(l) < 2:
        # If series has less than 2 elements, return 0 as there's no increase
        return 0, 0, 0, 0, 0

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
    return nbDaysBuy, buyAt, nbDaysSell, sellAt, stopLoss


def printHeader(company):
    print(f"{company[TICKER]:>4}:", end=" ")
    for date in company[DATES]:
        print(
            f"{str(date[DAY]) + calendar.month_name[date[MONTH]][:3]:^20}", end="    "
        )
    print()


def getMask(mask, company, stock, lookBack=6):
    printHeader(company)
    today = datetime.now()
    for year in range(today.year - lookBack, today.year):
        # TODO fix manual range (default value)
        print(year, end=": ")
        for date in company[DATES]:
            esppDate = datetime(year, date[MONTH], date[DAY])
            curMask = (stock.index >= esppDate - timedelta(days=1)) & (
                stock.index <= esppDate + timedelta(days=60)
            )
            a, b, c, d, e = stats(stock.loc[curMask, ADJCLOSE])
            print(f"{a:2} {-b:4.0%} {c:2} {d:3.0%} {-e:4.0%}", end="    ")
            mask |= curMask
        print()
    print()
    return mask


def within(company, timeDuration):
    today = datetime.now()
    xTimeAgo = today - timedelta(days=5)
    xTimeFromNow = today + timeDuration
    return any(
        xTimeAgo <= datetime(today.year, date[MONTH], date[DAY]) <= xTimeFromNow
        # this to check if the date might not be next year
        or xTimeAgo <= datetime(today.year + 1, date[MONTH], date[DAY]) <= xTimeFromNow
        for date in company[DATES]
    )


def neverDownloaded(company):
    return DOWNLOAD not in company


def lastDownloadOverOneYearAgo(company):
    return datetime.strptime(
        company[DOWNLOAD], DATEFORMAT
    ) < datetime.today() - timedelta(weeks=52)


def needToDownload(company):
    return (
        neverDownloaded(company)
        or lastDownloadOverOneYearAgo(company)
        # TODO fix this shit below
        or any(
            # 2 months ago
            datetime.today() - timedelta(weeks=9) <
            # company espp date
            datetime(datetime.today().year, date[MONTH], date[DAY]) <
            # last download
            datetime.strptime(company[DOWNLOAD], DATEFORMAT) <
            # today
            datetime.today()
            for date in company[DATES]
        )
    )


def main():
    dataFilename = "data.json"
    with open(dataFilename) as file:
        companies = json.load(file)
    # update if necessary
    for _name, company in companies.items():
        csvName = "prices/" + company[TICKER] + ".csv"
        if needToDownload(company):
            # TODO add CLI option to force download
            data = yf.download(company[TICKER])
            today = datetime.today().strftime(DATEFORMAT)
            companies[_name][DOWNLOAD] = today
            with open(dataFilename, "w") as file:
                json.dump(companies, file, indent=2)
            data.to_csv(csvName)

    fromNow = timedelta(days=15)
    companies = {
        name: comp for name, comp in companies.items() if within(comp, fromNow)
    }
    colors = iter(cm.rainbow(np.linspace(0, 1, len(companies))))
    # plot
    for name, company in companies.items():
        csvName = "prices/" + company[TICKER] + ".csv"
        color = next(colors)
        # only plot/analyze if the company has an espp date within 2 months in the past or future
        stock = pd.read_csv(csvName, index_col=0, parse_dates=True)
        # build mask + show stats
        mask = getMask(pd.Series(False, index=stock.index), company, stock)
        # plotIt ( maybe )
        stock.loc[~mask, ADJCLOSE] = None
        plotIt(company[TICKER], stock, color)

    print("buy after n days at -x% and sell after m days at +y% and accept -z% loss.")
    plt.show()


if __name__ == "__main__":
    main()
