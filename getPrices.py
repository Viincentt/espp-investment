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
    parser.add_argument(
        TP,
        help="Take Profit percentage. Use lowest historical profit - 1% to maximize chances to hit",
    )
    parser.add_argument(
        SL,
        help="Stop Loss percentage. Use highest historical loss + 1% to maximize space for errors",
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest=limit,
        help="Limit Order percentage. Use lowest historical loss to maximixe chances order execute",
        metavar="PERCENT",
    )

    args = parser.parse_args()
    SL, TP, price = float(args.SL), float(args.TP), float(args.price)
    if args.limit:
        price *= 1 - float(args.limit)
    TP = round(price * (1 + TP), 2)
    SL = round(price * (1 - SL), 2)
    print("Buy at", round(price, 2), "Take Profit at", TP, "Stop Loss at", SL)


if __name__ == "__main__":
    main()
