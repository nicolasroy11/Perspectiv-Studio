import axios from "axios";
import { useQuery } from "@tanstack/react-query";

// Base URL of your FastAPI backend
const BASE_URL = "http://localhost:8000/api";

export async function fetchOhlcv(limit = 30000) {
  const res = await axios.get(`${BASE_URL}/ohlcv?limit=${limit}`);
  return res.data.data;
}

export async function fetchEval(limit = 20000) {
  const res = await axios.get(`${BASE_URL}/eval?limit=${limit}`);
  return res.data.data;
}

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
