import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import anomalyService from "@/services/anomaly/anomalyService";
import transactionService from "@/services/transaction/transactionService";
import { AnomalyResult, Transaction } from "@/types";

export const useAnomalyData = () => {
    const { transactionId } = useParams<{ transactionId: string }>();
    const [anomaly, setAnomaly] = useState<AnomalyResult | null>(null);
    const [transaction, setTransaction] = useState<Transaction | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!transactionId) return;

        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                console.log("Fetching anomaly for transaction ID:", transactionId);
                const anomalyData = await anomalyService.getByTransactionId(transactionId);
                console.log("Anomaly data fetched:", anomalyData);
                setAnomaly(anomalyData);

                try {
                    console.log("Fetching transaction details for:", transactionId);
                    const txData = await transactionService.getById(anomalyData.transactionHash);
                    console.log("Transaction data fetched:", txData);
                    setTransaction(txData);
                } catch (txErr) {
                    console.warn("Failed to fetch transaction:", txErr);
                }
            } catch (err) {
                console.error("Failed to fetch anomaly:", err);
                setError(err instanceof Error ? err.message : "Failed to load anomaly details");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [transactionId]);

    return { anomaly, transaction, loading, error, transactionId };
};
