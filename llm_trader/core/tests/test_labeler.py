import pandas as pd
from llm_trader.core import labeler

def test_label_trades_only_labels_setups():
    df = pd.DataFrame({
        "high": [1.101, 1.102, 1.104, 1.107, 1.110],
        "low": [1.099, 1.098, 1.097, 1.096, 1.095],
        "close": [1.100, 1.101, 1.103, 1.106, 1.109],
        "setup": [True, False, False, False, False],
    })
    labeled = labeler.label_trades(df, reward_pips=3, risk_pips=3, lookahead=3)
    assert labeled.loc[0, "outcome"] in {1, 0, -1}
    assert labeled.loc[1:, "outcome"].isna().all()

def test_label_trades_target_hits_first():
    df = pd.DataFrame({
        "high": [1.100, 1.104, 1.108, 1.090],
        "low": [1.099, 1.099, 1.099, 1.089],
        "close": [1.099, 1.104, 1.107, 1.090],
        "setup": [True, False, False, False],
    })
    labeled = labeler.label_trades(df, reward_pips=3, risk_pips=3, lookahead=3)
    assert labeled.loc[0, "outcome"] == 1
