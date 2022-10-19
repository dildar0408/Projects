import pandas as pd
import yfinance as yf
import datetime as datetime
import math

def get_prices():

    with open('price_data.csv') as f:
        price_data = pd.read_csv(f)

    price_data = price_data.pivot(index="DATE_",columns="TICKER",values="PRICE")

    price_data = price_data.rename(columns={
                                            'CommodityIndex|SPGSCITR': "Commodities|SPGSCITR",
                                            'EquityIndex|EAFE': "Equities|EAFE",
                                            'EquityIndex|MXEF': "Equities|MXEF",
                                            'EquityIndex|SPX': "Equities|SPX",
                                            'FXIndex|DXY Index': "Currencies|DXY",
                                            'FixedIncomeIndex|JPMTUS': "Fixed Income|JPMTUS",
                                            'NominalGovBond|USDUSA': "3M Treasury Rate"
                                           })

    price_data.index = pd.to_datetime(price_data.index, infer_datetime_format=True)
    price_data = price_data.sort_index(axis = 0)

    return price_data

def calc_returns(prices, lp, hp):
    tickers = ['Commodities|SPGSCITR', 'Equities|EAFE', 'Equities|MXEF',
       'Equities|SPX', 'Currencies|DXY', 'Fixed Income|JPMTUS']
    rets = prices[tickers].pct_change()
    excess_rets = rets.sub(prices['3M Treasury Rate'].diff()/100, axis=0).dropna()
    excess_rets_cum = (1+excess_rets).cumprod()

    excess_rets_cum_m = excess_rets_cum.groupby([excess_rets_cum.index.year, excess_rets_cum.index.month], as_index=True).last()
    index = excess_rets_cum_m.index.to_flat_index().to_series()
    index = index.apply(lambda x: x + (28,))
    index = index.apply(lambda x: datetime.date(*x))
    excess_rets_cum_m.set_index(index, inplace=True)
    excess_rets_cum_m.index = pd.to_datetime(excess_rets_cum_m.index)
    excess_rets_cum_m.index = excess_rets_cum_m.index.to_period('M')

    excess_rets_lb = (excess_rets_cum_m/excess_rets_cum_m.shift(lp)-1).dropna()
    excess_rets_hp = excess_rets_cum_m/excess_rets_cum_m.shift(hp)-1
    excess_rets_hp = excess_rets_hp.loc[excess_rets_lb.index]

    return excess_rets_lb, excess_rets_hp

def calc_ex_ante_volatilities(prices, delta):
    '''
    tickers = ['Commodities|SPGSCITR', 'Equities|EAFE', 'Equities|MXEF',
       'Equities|SPX', 'Currencies|DXY', 'Fixed Income|JPMTUS']
    rets = prices[tickers].pct_change()
    excess_rets = rets.sub(prices['3M Treasury Rate'].diff()/100, axis=0).dropna()

    # Initialize exponetially weighted average returns
    ewar = pd.DataFrame(index=excess_rets.index[excess_rets.index.year > 2004], columns = excess_rets.columns) 
    # Initialize ex ante volatilities
    ea_vol = pd.DataFrame(index=excess_rets.index[excess_rets.index.year > 2004], columns = excess_rets.columns)
    for idx in ewar.index:
        for col in ewar.columns:
            ewar.loc[idx,col] = 0
            ea_vol.loc[idx,col] = 0
            excess_rets_t = excess_rets.loc[excess_rets.index < idx,col].tail(261)
            for i, row in enumerate(excess_rets_t.reindex().sort_index(ascending=False)):  
                ewar.loc[idx,col] += (1-delta)*(delta**i)*row
            for i, row in enumerate(excess_rets_t.reindex().sort_index(ascending=False)):  
                ea_vol.loc[idx,col] += (1-delta)*(delta**i)*((row-ewar.loc[idx,col])**2)
            ea_vol.loc[idx,col] = math.sqrt(261*ea_vol.loc[idx,col])
    
    ea_vol = ea_vol.groupby([ea_vol.index.year, ea_vol.index.month], as_index=True).last()
    index = ea_vol.index.to_flat_index().to_series()
    index = index.apply(lambda x: x + (28,))
    index = index.apply(lambda x: datetime.date(*x))
    ea_vol.set_index(index, inplace=True)
    ea_vol.index = pd.to_datetime(ea_vol.index)
    ea_vol.index = ea_vol.index.to_period('M')

    filepath = Path('C:/Users/ghotrad2/Desktop/Personal/Prep/Interview Preparation/Projects and Courses/Projects/6. Time Series Momentum/ea_vol.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True) 
    ea_vol.to_csv(filepath)  

    '''
    with open('ea_vol.csv') as f:
        ea_vol = pd.read_csv(f)
    ea_vol = ea_vol.set_index('Unnamed: 0')
    ea_vol.index = pd.to_datetime(ea_vol.index)
    ea_vol.index = ea_vol.index.to_period('M')

    return ea_vol



