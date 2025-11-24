"use client";

import Plot from "react-plotly.js";
import type { RsiLowriderCandleState } from "@/types/RsiLowriderCandleState";

interface LowriderCandleChartProps {
  data: RsiLowriderCandleState[];
}

export default function RsiLowriderCandleChart({ data }: LowriderCandleChartProps) {
  if (!data || data.length === 0) {
    return <div>No backtest data.</div>;
  }

  // --- Common x-axis (timestamps) ---
  const times = data.map((d) => d.timestamp);

  // --- Candlestick trace ---
  const candleTrace = {
    x: times,
    open: data.map((d) => d.open),
    high: data.map((d) => d.high),
    low: data.map((d) => d.low),
    close: data.map((d) => d.close),
    type: "candlestick" as const,
    name: "Price",
  };

  // --- Equity curve (secondary y-axis) ---
  const equityTrace = {
    x: times,
    y: data.map((d) => d.equity),
    type: "scatter" as const,
    mode: "lines" as const,
    name: "Equity",
    yaxis: "y2",
    line: {
      width: 1.5,
    },
  };

  // --- Anchor entries (green triangles) ---
  const anchorPoints = data.filter((d) => d.anchor_triggered);
  const anchorTrace = {
    x: anchorPoints.map((d) => d.timestamp),
    y: anchorPoints.map((d) => d.close),
    type: "scatter" as const,
    mode: "markers" as const,
    name: "Anchor Entry",
    marker: {
      symbol: "triangle-up",
      size: 10,
      color: "rgba(34,197,94,0.9)", // green
    },
    hoverinfo: "x+y+name",
  };

  // --- Rungs added (blue dots) ---
  const rungPoints = data.filter((d) => d.rung_added !== null && d.rung_added !== undefined);
  const rungTrace = {
    x: rungPoints.map((d) => d.timestamp),
    // rung entries are always below the current close; we can either:
    // - reconstruct from entry_prices, or
    // - just plot at close for now for visual context.
    // If you want exact rung prices, we can refine this later.
    y: rungPoints.map((d) => d.close),
    type: "scatter" as const,
    mode: "markers" as const,
    name: "Rung Added",
    marker: {
      symbol: "circle",
      size: 8,
      color: "rgba(59,130,246,0.9)", // blue
    },
    hoverinfo: "x+y+name+text",
    text: rungPoints.map((d) => `Rung #${d.rung_added}`),
  };

  // --- TP hits (if you log them as events like "TP_HIT") ---
  const tpPoints = data.filter((d) => d.events?.includes("TP_HIT"));
  const tpTrace = {
    x: tpPoints.map((d) => d.timestamp),
    y: tpPoints.map((d) => d.close),
    type: "scatter" as const,
    mode: "markers" as const,
    name: "TP Hit",
    marker: {
      symbol: "star",
      size: 10,
      color: "rgba(250,204,21,0.95)", // yellow/gold
    },
    hoverinfo: "x+y+name",
  };

  const layout: Partial<Plotly.Layout> = {
    title: { text: "RSI Lowrider – Backtest" },
    plot_bgcolor: "#0f172a",
    paper_bgcolor: "#0f172a",
    font: { color: "#e2e8f0" },
    showlegend: true,
    legend: {
      orientation: "h",
      x: 0,
      y: 1.1,
    },
    xaxis: {
      rangeslider: { visible: false },
      title: { text: "Time" },
    },
    yaxis: {
      title: { text: "Price" },
      domain: [0.25, 1], // top 75% for price
    },
    yaxis2: {
      title: { text: "Equity" },
      anchor: "x",
      overlaying: "y",
      side: "right",
      showgrid: false,
    },
    margin: { t: 60, l: 60, r: 60, b: 40 },
    height: 700,
  };

  const plotData: any[] = [
    candleTrace,
    equityTrace,
    anchorTrace,
    rungTrace,
    tpTrace,
  ];

  return (
    <Plot
      data={plotData}
      layout={layout}
      config={{ responsive: true }}
      className="w-full"
    />
  );
}
