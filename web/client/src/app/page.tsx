"use client";

import { useOhlcvData, useEvalData } from "../lib/api";
import CandleChart from "../components/CandleChart.client";
import StatsPanel from "../components/StatsPanel";


export default function Home() {
  const { data: ohlcv, isLoading: ohlcvLoading } = useOhlcvData();
  const { data: evals, isLoading: evalLoading } = useEvalData();

  if (ohlcvLoading || evalLoading)
    return <div className="p-8 text-gray-400">Loading chart…</div>;

  if (!ohlcv || !evals)
    return <div className="p-8 text-red-500">Failed to load data.</div>;

  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold mb-4 text-blue-400">Perspectiv Trader Dashboard</h1>
      <StatsPanel />
      <CandleChart priceData={ohlcv} decisionData={evals} />
    </main>
  );
}
