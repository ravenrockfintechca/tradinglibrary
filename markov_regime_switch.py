from hmmlearn.hmm import GaussianHMM
def markov_regime(prices, n_states=2):
    model = GaussianHMM(n_components=n_states).fit(prices.pct_change().dropna().values.reshape(-1,1))
    return model.predict(prices.pct_change().fillna(0).values.reshape(-1,1))