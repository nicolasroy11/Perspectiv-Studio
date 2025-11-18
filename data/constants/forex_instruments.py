from data.models.forex_instrument import ForexInstrument


class ForexInstruments:

    EURUSD = ForexInstrument(
        symbol="EURUSD",
        pip_size=0.0001,
        dollars_per_pip_per_lot=10.0,
        description="Euro vs US Dollar"
    )

    GBPJPY = ForexInstrument(
        symbol="GBPJPY",
        pip_size=0.01,
        dollars_per_pip_per_lot=9.17,   # approximate, varies by price
        description="British Pound vs Japanese Yen"
    )
