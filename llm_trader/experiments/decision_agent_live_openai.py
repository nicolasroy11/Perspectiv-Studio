from llm_trader.intelligence.decision_agent import DecisionAgent
from llm_trader.intelligence.context_summarizer import ContextSummary, FeatureSet, TrendState, RsiZone
from llm_trader.intelligence.openai_client import OpenAILLM
import runtime_settings

# --- Use a real LLM backend ---
llm = OpenAILLM(model="gpt-4o-mini", api_key=runtime_settings.OPENAI_API_KEY)

agent = DecisionAgent(llm)

# --- Example summarized context (could come from ContextSummarizer) ---
features = FeatureSet(
    close=1.1063, high=1.1071, low=1.1055, open=1.1060, volume=1780,
    rsi=27.3, ema_fast=1.1059, ema_slow=1.1065, adx=24.8, atr=0.00032,
    trend_state=TrendState.DOWN, rsi_zone=RsiZone.OVERSOLD,
    last_n_green=2, last_n_red=3, atr_rank_pct=0.42
)
context = ContextSummary(
    text="Trend down, RSI oversold, approaching prior demand zone.",
    features=features,
)

# --- Evaluate a setup ---
decision = agent.evaluate(context, setup_name="RSI_Reversal", rr_ratio=1.8, lookahead_bars=12)

print("\n=== RAW LLM RESPONSE ===")
print(decision.as_dict())
