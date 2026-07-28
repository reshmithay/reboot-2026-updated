import React from "react";
import { AnomalyResult } from "@/types";

interface AnomalyReasonsCardProps {
    anomaly: AnomalyResult;
}

export const AnomalyReasonsCard: React.FC<AnomalyReasonsCardProps> = ({ anomaly }) => {
    if (!anomaly.anomalyReasons || anomaly.anomalyReasons.length === 0) {
        return (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Reasons</h2>
                <p className="text-sm text-gray-600">No specific reasons available for this anomaly.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Reasons</h2>
            <div className="space-y-3">
                {anomaly.anomalyReasons.map((reason, index) => (
                    <div
                        key={index}
                        className="p-4 bg-red-50 border border-red-200 rounded-lg"
                    >
                        <div className="flex items-start gap-2">
                            <svg className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <div className="flex-1">
                                <div className="text-sm font-medium text-red-900">{reason.reasonCode}</div>
                                <div className="text-sm text-red-700 mt-1">{reason.description}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
