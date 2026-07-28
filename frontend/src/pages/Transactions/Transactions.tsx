import React, { useEffect, useState } from "react";
import transactionService, { Transaction } from "../../services/transaction/transactionService";
import { formatDate } from "../../utilities/helpers/dateHelper";
import { SUPPORTED_CHAINS } from "../../utilities/constants/appConstants";

const Transactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAnomaliesOnly, setShowAnomaliesOnly] = useState(false);

  const fetchTransactions = (anomalyFilter?: boolean) => {
    setLoading(true);
    transactionService
      .list({ page: 1, page_size: 50, is_anomaly: anomalyFilter })
      .then((res) => setTransactions(res.items || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTransactions(showAnomaliesOnly || undefined);
  }, [showAnomaliesOnly]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Transactions</h1>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={showAnomaliesOnly}
            onChange={(e) => setShowAnomaliesOnly(e.target.checked)}
            className="rounded"
          />
          Show anomalies only
        </label>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading transactions...</p>
      ) : transactions.length === 0 ? (
        <p className="text-gray-400">No transactions found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-800">
                <th className="text-left py-3 px-4">Tx Hash</th>
                <th className="text-left py-3 px-4">From</th>
                <th className="text-left py-3 px-4">To</th>
                <th className="text-left py-3 px-4">Value</th>
                <th className="text-left py-3 px-4">Chain</th>
                <th className="text-left py-3 px-4">Risk Score</th>
                <th className="text-left py-3 px-4">Time</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr
                  key={tx.id}
                  className="border-b border-gray-800 hover:bg-gray-900"
                >
                  <td className="py-3 px-4 font-mono text-xs">{tx.transaction_hash.slice(0, 14)}...</td>
                  <td className="py-3 px-4 font-mono text-xs">{tx.from_wallet_address?.slice(0, 10) || "N/A"}...</td>
                  <td className="py-3 px-4 font-mono text-xs">{tx.to_wallet_address?.slice(0, 10) || "N/A"}...</td>
                  <td className="py-3 px-4">{tx.amount || 0} {tx.token_symbol || tx.currency}</td>
                  <td className="py-3 px-4">{tx.chain_id ? (SUPPORTED_CHAINS[tx.chain_id] || `Chain ${tx.chain_id}`) : "N/A"}</td>
                  <td className="py-3 px-4">
                    <span className="text-gray-500">-</span>
                  </td>
                  <td className="py-3 px-4 text-gray-400">{formatDate(tx.transaction_timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Transactions;
