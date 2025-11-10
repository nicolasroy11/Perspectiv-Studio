"use client";

import dynamic from "next/dynamic";

// Dynamically import Plotly to prevent SSR crash (“self is not defined”)
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface CandleChartProps {
  priceData: any[];
  decisionData: any[];
}

export default function CandleChart({ priceData, decisionData }: CandleChartProps) {
  if (!priceData?.length) return <div>No price data.</div>;

  // --- Candlestick trace ---
  const candleTrace = {
    x: priceData.map((d) => d.timestamp),
    open: priceData.map((d) => d.open),
    high: priceData.map((d) => d.high),
    low: priceData.map((d) => d.low),
    close: priceData.map((d) => d.close),
    type: "candlestick" as const,
    name: "Price",
  } as any;

  // --- LLM Decision markers ---
  const decisionTraces = ["ENTER", "SKIP", "REVERSE"].map((act) => {
    const subset = decisionData.filter((d) => d.action === act);
    return {
      x: subset.map((d) => d.end_time),
      y: subset.map((d) => {
        const candle = priceData.find((p) => p.timestamp >= d.end_time);
        return candle ? candle.close : priceData[priceData.length - 1].close;
      }),
      mode: "markers" as const,
      type: "scatter" as const,
      name: act,
      marker: {
        size: 8,
        color:
          act === "ENTER"
            ? "green"
            : act === "SKIP"
            ? "red"
            : "purple",
        opacity: 0.7,
      },
      text: subset.map(
        (d) =>
          `${act} | conf: ${(d.confidence ?? 0).toFixed(2)}\n${d.rationale}`
      ),
      hoverinfo: "text+x+y",
    } as any;
  });

  // --- Chart layout ---
  const layout = {
    title: { text: "LLM Trader — Price & Decisions" },
    plot_bgcolor: "#0f172a",
    paper_bgcolor: "#0f172a",
    font: { color: "#e2e8f0" },
    xaxis: {
      rangeslider: { visible: false },
      title: { text: "Time" },
    },
    yaxis: {
      title: { text: "Price" },
    },
    margin: { t: 60, l: 60, r: 20, b: 40 },
    height: 700,
  } as any;

  // --- Render Plotly chart ---
  return (
    <Plot
      data={[candleTrace, ...decisionTraces]}
      layout={layout}
      config={{ responsive: true }}
      className="w-full"
    />
  );
}
