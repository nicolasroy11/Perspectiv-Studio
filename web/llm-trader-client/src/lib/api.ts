import axios from "axios";
import { useQuery } from "@tanstack/react-query";

// -----------------------------------------------------------------------------
// Base URL
// -----------------------------------------------------------------------------
const BASE_URL = "http://54.184.251.12:8000/api";

// -----------------------------------------------------------------------------
// Fetch helpers
// -----------------------------------------------------------------------------
export async function fetchOhlcv(limit = 30000) {
  const res = await axios.get(`${BASE_URL}/ohlcv?limit=${limit}`);
  return res.data.data;
}

export async function fetchEval(limit = 20000) {
  const res = await axios.get(`${BASE_URL}/eval?limit=${limit}`);
  return res.data.data;
}

export async function fetchEvalStats() {
  const res = await axios.get(`${BASE_URL}/eval/stats`);
  return res.data;
}

// -----------------------------------------------------------------------------
// React Query hooks
// -----------------------------------------------------------------------------
export function useOhlcvData(limit = 30000) {
  return useQuery({
    queryKey: ["ohlcv", limit],
    queryFn: () => fetchOhlcv(limit),
  });
}

export function useEvalData(limit = 20000) {
  return useQuery({
    queryKey: ["eval", limit],
    queryFn: () => fetchEval(limit),
  });
}

export function useEvalStats() {
  return useQuery({
    queryKey: ["evalStats"],
    queryFn: fetchEvalStats,
    refetchInterval: 60_000, // auto-refresh every 60s if you want live updates
  });
}
