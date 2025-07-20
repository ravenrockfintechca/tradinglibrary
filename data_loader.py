import yfinance as yf

def load_data(ticker, start='2022-01-01'):
    return yf.download(ticker, start=start)['Close']
