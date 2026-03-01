"""
The simplest version of the quant-research framework
Using a trend-following strategy
"""

from argparse import ArgumentParser

from quant_research.core import Backtest, load_data, Metrics
from quant_research.strategies import TrendStrategy


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-t", "--ticker", type=str, required=True)
    parser.add_argument("-p", "--period", type=str, default="1y")
    parser.add_argument("-i", "--interval", type=str, default="1d")
    return parser.parse_args()


def main():
    args = parse_arguments()
    data = load_data(args.ticker, args.period, args.interval)
    strategy = TrendStrategy(data, TrendStrategy.TrendStrategyConfig())
    backtest = Backtest(strategy)
    metrics = Metrics(backtest.run())
    result = metrics.evaluate()
    print(result)


if __name__ == "__main__":
    main()
