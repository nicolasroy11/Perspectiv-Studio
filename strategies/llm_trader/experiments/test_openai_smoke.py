from __future__ import annotations
from strategies.llm_trader.intelligence.openai_client import OpenAILLM

def main() -> None:
    llm = OpenAILLM(model="gpt-4o-mini")  # or any model you prefer
    out = llm("Reply with the single word: OK")
    print("LLM:", out)

if __name__ == "__main__":
    main()
