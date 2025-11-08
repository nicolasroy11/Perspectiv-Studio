"use client";

import Plot from "react-plotly.js";

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
    type: "candlestick",
    name: "Price",
  };

  // --- LLM Decision markers ---
  const decisionTraces = ["ENTER", "SKIP", "REVERSE"].map((act) => {
    const subset = decisionData.filter((d) => d.action === act);
    return {
      x: subset.map((d) => d.end_time),
      y: subset.map((d) => {
        // TODO: find matching close price for approximate marker placement; imoprove based on exact timestamp
        const candle = priceData.find((p) => p.timestamp >= d.end_time);
        return candle ? candle.close : priceData[priceData.length - 1].close;
      }),
      mode: "markers",
      type: "scatter",
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
    };
  });

  const layout = {
    title: "LLM Trader — Price & Decisions",
    plot_bgcolor: "#0f172a",
    paper_bgcolor: "#0f172a",
    font: { color: "#e2e8f0" },
    xaxis: {
      rangeslider: { visible: false },
      title: "Time",
    },
    yaxis: {
      title: "Price",
    },
    margin: { t: 60, l: 60, r: 20, b: 40 },
    height: 700,
  };

  return (
    <Plot
      data={[candleTrace, ...decisionTraces]}
      layout={layout}
      config={{ responsive: true }}
      className="w-full"
    />
  );
}
