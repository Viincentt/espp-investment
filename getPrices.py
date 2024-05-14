from argparse import ArgumentParser

"""
parser.add_argument(
    "-f", "--file", dest="filename", help="write report to FILE", metavar="FILE"
)
parser.add_argument(
    "-q",
    "--quiet",
    action="store_false",
    dest="verbose",
    default=True,
    help="don't print status messages to stdout",
)
"""


def main():
    parser = ArgumentParser()
    SL, TP, price, limit = "SL", "TP", "price", "limit"
    parser.add_argument(price, help="Current price of stock")
    parser.add_argument(TP, help="Take Profit percentage")
    parser.add_argument(SL, help="Stop Loss percentage")
    parser.add_argument(
        "-l", "--limit", dest=limit, help="Limit Order percentage", metavar="PERCENT"
    )

    args = parser.parse_args()
    SL, TP, price, limit = (
        float(args.SL),
        float(args.TP),
        float(args.price),
        float(args.limit),
    )
    if args.limit:
        price *= 1 - limit
    TP = price * (1 + TP)
    SL = price * (1 - SL)
    print("Buy at", price, "Take Profit at", TP, "Stop Loss at", SL)


if __name__ == "__main__":
    main()
