/**
 * Narrative Personas
 * 
 * Defines role-based personas for AI-generated narratives.
 * Each persona generates narratives with different styles and terminology
 * appropriate for their audience.
 */

export interface Persona {
  key: string;
  label: string;
  description: string;
  icon: string;
}

export const NARRATIVE_PERSONAS: Persona[] = [
  {
    key: "fraud-analyst",
    label: "Fraud Analyst",
    description: "Analytical, detailed, pattern-focused narrative with full technical details",
    icon: "ExperimentOutlined",
  },
  {
    key: "compliance-officer",
    label: "Compliance Officer",
    description: "Internal alert with regulatory terminology and action items",
    icon: "SafetyOutlined",
  },
  {
    key: "relationship-manager",
    label: "Relationship Manager",
    description: "Customer-friendly, neutral tone without accusatory language",
    icon: "UserOutlined",
  },
  {
    key: "auditor",
    label: "Auditor",
    description: "Technical, transparent narrative with full traceability and metrics",
    icon: "LineChartOutlined",
  },
  {
    key: "regulator",
    label: "FCA / Regulator",
    description: "Formal, evidence-based report suitable for regulatory submission",
    icon: "SafetyCertificateOutlined",
  },
];

export const DEFAULT_PERSONA = "fraud-analyst";

/**
 * Get persona by key
 */
export const getPersona = (key: string): Persona | undefined => {
  return NARRATIVE_PERSONAS.find((p) => p.key === key);
};

/**
 * Get all persona keys
 */
export const getPersonaKeys = (): string[] => {
  return NARRATIVE_PERSONAS.map((p) => p.key);
};
