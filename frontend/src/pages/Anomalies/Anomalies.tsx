import React, { useEffect, useState } from "react";
import anomalyService, { Anomaly } from "../../services/anomaly/anomalyService";
import { getSeverityBadgeClass, formatScore } from "../../utilities/formatters/riskFormatter";
import { formatRelative } from "../../utilities/helpers/dateHelper";

const Anomalies: React.FC = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    anomalyService
      .list({ page: 1, page_size: 50 })
      .then((res) => setAnomalies(res.items || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <h1 className="text-2xl font-bold mb-6">Detected Anomalies</h1>

      {loading ? (
        <p className="text-gray-400">Loading anomalies...</p>
      ) : anomalies.length === 0 ? (
        <p className="text-gray-400">No anomalies detected yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-800">
                <th className="text-left py-3 px-4">ID</th>
                <th className="text-left py-3 px-4">Transaction</th>
                <th className="text-left py-3 px-4">Score</th>
                <th className="text-left py-3 px-4">Severity</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Detected</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((a) => (
                <tr key={a.id} className="border-b border-gray-800 hover:bg-gray-900">
                  <td className="py-3 px-4 font-mono text-xs">{a.id.slice(0, 12)}...</td>
                  <td className="py-3 px-4 font-mono text-xs">{a.transaction_id.slice(0, 16)}...</td>
                  <td className="py-3 px-4">{formatScore(a.score)}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded border text-xs font-medium ${getSeverityBadgeClass(a.severity)}`}>
                      {a.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 capitalize">{a.status}</td>
                  <td className="py-3 px-4 text-gray-400">{formatRelative(a.detected_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Anomalies;
