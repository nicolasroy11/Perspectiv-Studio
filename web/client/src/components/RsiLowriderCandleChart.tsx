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

  // --- Equity curve ---
  const equityTrace = {
    x: times,
    y: data.map((d) => d.equity),
    type: "scatter" as const,
    mode: "lines",
    name: "Equity",
    yaxis: "y2",
    line: { width: 1.4 },
  };

  // --- ANCHOR entries ---
  const anchorPoints = data.filter((d) => d.events.includes("ANCHOR"));
  const anchorTrace = {
    x: anchorPoints.map((d) => d.timestamp),
    y: anchorPoints.map((d) => d.close),
    type: "scatter",
    mode: "markers",
    name: "Anchor",
    marker: {
      symbol: "triangle-up",
      size: 10,
      color: "rgba(34,197,94,0.9)",
    },
  };

  // --- RUNG_ADDED events ---
  const rungAddedPoints = data.filter((d) => d.events.includes("RUNG_ADDED"));
  const rungAddedTrace = {
    x: rungAddedPoints.map((d) => d.timestamp),
    y: rungAddedPoints.map((d) => d.close),
    type: "scatter",
    mode: "markers",
    name: "Rung Added",
    marker: {
      symbol: "circle",
      size: 8,
      color: "rgba(59,130,246,0.9)",
    },
    hoverinfo: "x+y+name",
  };

  // --- TP_HIT events ---
  const tpHitPoints = data.filter((d) => d.events.includes("TP_HIT"));
  const tpHitTrace = {
    x: tpHitPoints.map((d) => d.timestamp),
    y: tpHitPoints.map((d) => d.close),
    type: "scatter",
    mode: "markers",
    name: "TP Hit",
    marker: {
      symbol: "star",
      size: 10,
      color: "rgba(250,204,21,0.95)",
    },
  };

  const layout: Partial<Plotly.Layout> = {
    title: { text: "RSI Lowrider — Backtest" },
    plot_bgcolor: "#0f172a",
    paper_bgcolor: "#0f172a",
    font: { color: "#e2e8f0" },
    xaxis: {
      rangeslider: { visible: false },
    },
    yaxis: { domain: [0.25, 1] },
    yaxis2: {
      overlaying: "y",
      side: "right",
      showgrid: false,
      title: "Equity",
    },
    legend: {
      orientation: "h",
      x: 0,
      y: 1.1,
    },
    height: 750,
  };

  const plotData = [
    candleTrace,
    equityTrace,
    anchorTrace,
    rungAddedTrace,
    tpHitTrace,
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
