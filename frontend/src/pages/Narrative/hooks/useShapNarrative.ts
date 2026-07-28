import { useState, useEffect } from "react";
import narrativeService, { NarrativeResponse } from "@/services/narrative/narrativeService";

export const useShapNarrative = (
    anomalyId: string | undefined, 
    autoGenerate: boolean = true,
    persona: string = "fraud-analyst"
) => {
    const [narrative, setNarrative] = useState<NarrativeResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const generateNarrative = async (topK: number = 5, selectedPersona?: string) => {
        if (!anomalyId) {
            setError("Anomaly ID is required");
            return;
        }

        try {
            setLoading(true);
            setError(null);
            
            console.log("Generating SHAP narrative for anomaly:", anomalyId, "with persona:", selectedPersona || persona);
            const response = await narrativeService.generateShapNarrative({
                anomaly_id: anomalyId,
                top_k: topK,
                persona: selectedPersona || persona,
            });
            
            console.log("Narrative generated:", response);
            setNarrative(response);
        } catch (err) {
            console.error("Failed to generate narrative:", err);
            setError(err instanceof Error ? err.message : "Failed to generate narrative");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (autoGenerate && anomalyId) {
            generateNarrative();
        }
    }, [anomalyId, autoGenerate, persona]);

    return { 
        narrative, 
        loading, 
        error, 
        generateNarrative,
        refetch: (selectedPersona?: string) => generateNarrative(5, selectedPersona),
    };
};
