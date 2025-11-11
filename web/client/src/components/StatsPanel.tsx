import { useEvalStats } from "../lib/api";

export default function StatsPanel() {
  const { data, isLoading, isError } = useEvalStats();

  if (isLoading)
    return (
      <div className="bg-perspectiv-panel p-4 rounded-xl text-perspectiv-muted">
        Loading stats…
      </div>
    );

  if (isError || !data)
    return (
      <div className="bg-perspectiv-panel p-4 rounded-xl text-perspectiv-danger">
        Error loading stats
      </div>
    );

  return (
    <div className="bg-perspectiv-panel border border-perspectiv-border rounded-xl p-5 w-64 shadow-md">

      <h2 className="text-perspectiv-accent font-semibold text-lg mb-4">
        LLM Decision Stats
      </h2>
      <div className="space-y-2 text-sm">
        <p>
          Total Decisions:{" "}
          <span className="font-medium text-perspectiv-text">{data.total}</span>
        </p>
        <p>
          ENTER: <span className="text-perspectiv-success">{data.enter}</span>
        </p>
        <p>
          SKIP: <span className="text-perspectiv-danger">{data.skip}</span>
        </p>
        <p>
          ENTER Ratio:{" "}
          <span className="text-perspectiv-accent">
            {(data.enter_ratio * 100).toFixed(1)}%
          </span>
        </p>
        <p>
          Avg Confidence:{" "}
          <span className="text-perspectiv-violet">
            {data.mean_confidence.toFixed(2)}
          </span>
        </p>
      </div>
    </div>
  );
}
