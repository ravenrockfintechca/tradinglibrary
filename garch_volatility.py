from arch import arch_model

def estimate_volatility(returns):
    model = arch_model(returns.dropna(), vol='Garch', p=1, q=1)
    return model.fit(disp='off').conditional_volatility
