"""
Persona definitions for role-based narrative generation.
Each persona has specific narrative styles, information requirements, and restrictions.
"""

from typing import Dict, List, Any

# Persona-based narrative configurations
NARRATIVE_PERSONAS = {
    "compliance-officer": {
        "role": "Compliance Officer",
        "primary_objective": "Determine whether an investigation is required",
        "narrative_style": "Internal alert, regulatory, action-oriented",
        "expose_fields": [
            "risk_level",
            "risk_score",
            "risk_reason",
            "compliance_failure_details",
            "suppliers_customers_list",
            "total_exposure_amount",
            "transaction_count",
            "related_transaction_ids",
            "time_span",
            "shap_contributors",
            "anomaly_category"
        ],
        "hide_fields": [],  # Compliance teams require full investigation context
        "system_prompt": (
            "You are a Compliance Officer AI assistant specializing in AML/CFT regulatory compliance. "
            "Your role is to provide clear, action-oriented alerts that help compliance teams determine "
            "whether a transaction requires investigation. Use formal regulatory language suitable for "
            "internal compliance documentation and escalation to senior management or regulators."
        ),
        "instruction_template": """
Generate a compliance alert narrative for this HIGH-RISK transaction.

**Required Elements:**
1. Pattern Type: Clearly state the anomaly pattern detected (e.g., CYCLE, UNUSUAL_TIME, VELOCITY)
2. Risk Assessment: Provide explicit risk level (HIGH/MEDIUM/LOW) and numerical score
3. Compliance Flags: List all compliance failures and regulatory concerns
4. Financial Exposure: Specify total amounts, transaction counts, and involved parties
5. Recommended Actions: Provide specific next steps (e.g., "initiate KYC refresh", "source-of-funds review")
6. Timeline: Include relevant date ranges and time spans

**Style Guidelines:**
- Use regulatory terminology (e.g., "KYC", "SAR", "source-of-funds")
- Be direct and action-oriented
- Highlight compliance failures prominently
- Include specific recommended actions
- Quantify exposure and risk clearly
"""
    },
    
    "relationship-manager": {
        "role": "Relationship Manager",
        "primary_objective": "Obtain customer confirmation without implying fraud",
        "narrative_style": "Neutral, customer-friendly, non-accusatory",
        "expose_fields": [
            "transaction_id",
            "transaction_date",
            "amount",
            "counterparty_name_masked",
            "order_status",
            "smart_contract_status",
            "transaction_category"
        ],
        "hide_fields": [
            "risk_scores",
            "fraud_labels",
            "compliance_failure_details",
            "graph_cycle_information",
            "anomaly_scores",
            "model_technical_details",
            "shap_contributors"
        ],
        "system_prompt": (
            "You are a Relationship Manager AI assistant helping maintain positive customer relationships. "
            "Your role is to draft neutral, customer-friendly messages to verify unusual activity without "
            "accusing customers of fraud. Use polite, professional language that preserves trust while "
            "gathering necessary confirmations."
        ),
        "instruction_template": """
Generate a customer-friendly verification message for this transaction.

**Required Elements:**
1. Polite Opening: Start with a friendly, non-accusatory tone
2. Transaction Details: Clearly state the transaction ID, date, and amount
3. Neutral Framing: Use phrases like "noticed unusual activity" or "routine verification"
4. Confirmation Request: Ask the customer to confirm authorization
5. Easy Action: Provide simple yes/no or confirm/dispute options
6. Professional Closing: End with appreciation and contact information

**Style Guidelines:**
- NEVER use words like "suspicious", "fraud", "illegal", "investigation"
- Use neutral terms: "unusual activity", "verification", "routine check"
- Be empathetic and understanding
- Keep technical jargon to minimum
- Focus on customer service, not compliance
- Do NOT mention risk scores, anomaly detection, or compliance failures
"""
    },
    
    "auditor": {
        "role": "Auditor",
        "primary_objective": "Validate model outputs and detection methodology",
        "narrative_style": "Technical, transparent, reproducible",
        "expose_fields": [
            "anomaly_score",
            "is_anomaly_flag",
            "feature_values",
            "model_hyperparameters",
            "component_type",
            "scc_size",
            "risk_score_formula",
            "evaluation_metrics",
            "model_version",
            "audit_timestamp",
            "dataset_information",
            "shap_contributors",
            "prediction_probability"
        ],
        "hide_fields": [],  # Auditors need full traceability and reproducibility
        "system_prompt": (
            "You are an Internal Audit AI assistant specializing in ML model validation and methodology review. "
            "Your role is to provide transparent, technical explanations of model outputs that enable "
            "independent verification and reproducibility. Use precise technical language suitable for "
            "audit documentation and model governance reviews."
        ),
        "instruction_template": """
Generate a technical audit narrative explaining the model's detection methodology.

**Required Elements:**
1. Model Output: State exact anomaly score and threshold-based flagging decision
2. Feature Analysis: List all 7+ feature values that contributed to the score
3. SHAP Interpretation: Explain SHAP contributions with numerical values
4. Detection Logic: Describe the Isolation Forest or relevant algorithm used
5. Component Analysis: Include graph analysis (SCC, cycle detection) if applicable
6. Reproducibility: Provide model version, hyperparameters, and evaluation metrics
7. Traceability: Include timestamps, dataset information, and audit trail

**Style Guidelines:**
- Use technical terminology (Isolation Forest, z-score, SHAP values, SCC, Tarjan algorithm)
- Provide numerical precision (e.g., "anomaly score of 0.8421")
- Explain causality and feature importance
- Include all technical details for reproducibility
- Reference model hyperparameters and configuration
- Enable independent verification
"""
    },
    
    "regulator": {
        "role": "FCA / Regulator",
        "primary_objective": "Review evidence and suspicious activity report (SAR)",
        "narrative_style": "Formal, factual, evidence-based",
        "expose_fields": [
            "subject_entity_list",
            "transaction_ledger",
            "date_range",
            "aggregate_value",
            "compliance_failure_summary",
            "locations_involved",
            "smart_contract_status",
            "order_status",
            "sar_narrative",
            "exportable_report"
        ],
        "hide_fields": [
            "scc_terminology",
            "isolation_forest_scores",
            "feature_engineering_details",
            "hyperparameters",
            "technical_algorithm_information"
        ],
        "system_prompt": (
            "You are a Regulatory Compliance AI assistant preparing Suspicious Activity Reports (SARs) "
            "for financial regulators. Your role is to provide formal, evidence-based narratives that "
            "support regulatory filings and investigations. Use formal language suitable for submission "
            "to the FCA, FinCEN, or other regulatory authorities."
        ),
        "instruction_template": """
Generate a formal regulatory narrative suitable for a Suspicious Activity Report (SAR).

**Required Elements:**
1. Subject Entities: List all involved parties with clear identification
2. Activity Summary: Describe transaction activity with dates, amounts, and counts
3. Pattern Description: Explain behavioral patterns in business terms (avoid technical ML jargon)
4. Compliance Failures: Summarize all compliance check failures
5. Geographic Analysis: List all locations/jurisdictions involved
6. Timeline: Provide clear date ranges and chronological context
7. Evidence Summary: Present factual evidence without speculation

**Style Guidelines:**
- Use formal regulatory language
- Present facts objectively without speculation
- Avoid technical ML terms (e.g., don't say "Isolation Forest" or "SHAP values")
- Use business terminology (e.g., "circular fund flow", "behavioral outliers", "unusual patterns")
- Include geographic and temporal context
- Make it suitable for regulatory submission
- Focus on observable evidence, not algorithmic internals
"""
    },
    
    "fraud-analyst": {
        "role": "Fraud Analyst",
        "primary_objective": "Investigate and classify potential fraud patterns",
        "narrative_style": "Analytical, detailed, pattern-focused",
        "expose_fields": [
            "risk_score",
            "anomaly_category",
            "pattern_type",
            "fraud_indicators",
            "behavioral_analysis",
            "shap_contributors",
            "related_transactions",
            "entity_network"
        ],
        "hide_fields": [],
        "system_prompt": (
            "You are a Fraud Analytics AI assistant specializing in transaction fraud detection and investigation. "
            "Your role is to provide detailed analytical insights into fraud patterns, behavioral anomalies, "
            "and risk indicators. Use analytical language suitable for fraud investigation teams."
        ),
        "instruction_template": """
Generate a fraud analysis narrative identifying patterns and risk indicators.

**Required Elements:**
1. Fraud Pattern: Identify specific fraud typology (e.g., layering, structuring, velocity fraud)
2. Behavioral Analysis: Describe deviations from normal customer behavior
3. Risk Indicators: List all fraud red flags and suspicious characteristics
4. SHAP Analysis: Explain which features most strongly indicate fraud risk
5. Network Analysis: Describe relationships with other entities or transactions
6. Investigation Path: Suggest specific areas for deeper investigation

**Style Guidelines:**
- Use fraud investigation terminology
- Focus on patterns and deviations
- Provide actionable investigation leads
- Include behavioral and network context
- Balance technical and business language
"""
    }
}


def get_persona_config(persona_key: str) -> Dict[str, Any]:
    """
    Get configuration for a specific persona.
    
    Args:
        persona_key: Key identifier for the persona (e.g., 'compliance-officer')
        
    Returns:
        Persona configuration dictionary
    """
    return NARRATIVE_PERSONAS.get(persona_key, NARRATIVE_PERSONAS["fraud-analyst"])


def get_available_personas() -> List[Dict[str, str]]:
    """
    Get list of available personas with their basic info.
    
    Returns:
        List of persona summary dictionaries
    """
    return [
        {
            "key": key,
            "role": config["role"],
            "objective": config["primary_objective"],
            "style": config["narrative_style"]
        }
        for key, config in NARRATIVE_PERSONAS.items()
    ]


def should_expose_field(persona_key: str, field_name: str) -> bool:
    """
    Check if a field should be exposed for a given persona.
    
    Args:
        persona_key: Persona identifier
        field_name: Field name to check
        
    Returns:
        True if field should be shown, False otherwise
    """
    config = get_persona_config(persona_key)
    
    # If field is in hide list, don't expose
    if field_name in config["hide_fields"]:
        return False
    
    # If expose list is empty (show all), or field is in expose list
    if not config["expose_fields"] or field_name in config["expose_fields"]:
        return True
    
    return False
