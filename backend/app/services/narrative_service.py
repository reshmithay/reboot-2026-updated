import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.clients.cortex_client import CortexClient
from app.schemas.narrative_schemas import ShapContributor, NarrativeResponse
from app.config.settings import settings
from app.constants.personas import get_persona_config, NARRATIVE_PERSONAS

logger = logging.getLogger(__name__)


class ShapNarrativeService:
    """Service for generating SHAP-based narratives using Cortex/Gemini."""

    def __init__(self):
        self.cortex_client = CortexClient()

    def generate_narrative(
        self,
        anomaly_id: str,
        shap_contributors: List[Dict[str, Any]],
        prediction_probability: float,
        prediction_label: str = "High Risk",
        top_k: int = 5,
        persona: str = "fraud-analyst",
    ) -> NarrativeResponse:
        """
        Generate an explainable narrative based on SHAP values and persona.

        Args:
            anomaly_id: Anomaly identifier
            shap_contributors: List of SHAP contributors (dicts)
            prediction_probability: Prediction probability (0-1)
            prediction_label: Risk label (e.g., "High Risk", "Medium Risk")
            top_k: Number of top contributors to include
            persona: Role-based persona (compliance-officer, relationship-manager, auditor, regulator, fraud-analyst)

        Returns:
            NarrativeResponse with generated explanation
        """
        # Get persona configuration
        persona_config = get_persona_config(persona)
        
        # Take top K contributors
        top_contributors = shap_contributors[:top_k]

        # Build the persona-specific prompt
        prompt = self._build_persona_prompt(
            shap_payload=top_contributors,
            prediction_probability=prediction_probability,
            prediction_label=prediction_label,
            persona_config=persona_config,
        )

        # Generate narrative using Cortex with persona-specific system message
        try:
            narrative_text = self.cortex_client.chat(
                prompt=prompt,
                system_message=persona_config["system_prompt"],
            )
        except Exception as e:
            logger.error(f"Failed to generate narrative via Cortex: {e}")
            # Fallback narrative
            narrative_text = self._generate_fallback_narrative(
                top_contributors, prediction_probability, prediction_label, persona_config
            )

        # Return response
        return NarrativeResponse(
            anomaly_id=anomaly_id,
            narrative=narrative_text,
            shap_contributors=top_contributors,
            prediction_probability=prediction_probability,
            prediction_label=prediction_label,
            model_used=settings.CORTEX_MODEL,
            generated_at=datetime.utcnow().isoformat(),
        )

    def _build_persona_prompt(
        self,
        shap_payload: List[Dict[str, Any]],
        prediction_probability: float,
        prediction_label: str,
        persona_config: Dict[str, Any],
    ) -> str:
        """Build persona-specific prompt for narrative generation."""
        
        # Base context
        base_context = f"""
**Prediction Label:** {prediction_label}
**Prediction Probability:** {prediction_probability:.2%}

**Top Risk Factors (SHAP Analysis):**
{json.dumps(shap_payload, indent=2)}
"""
        
        # Combine with persona-specific instructions
        prompt = persona_config["instruction_template"] + "\n\n" + base_context
        
        return prompt

    def _generate_fallback_narrative(
        self,
        shap_contributors: List[Dict[str, Any]],
        prediction_probability: float,
        prediction_label: str,
        persona_config: Dict[str, Any],
    ) -> str:
        """Generate a basic narrative when Cortex is unavailable."""
        persona_role = persona_config.get("role", "Analyst")
        
        if "Relationship Manager" in persona_role:
            # Customer-friendly fallback
            narrative_parts = [
                "We noticed some unusual activity on this transaction and wanted to reach out to you.",
                "\nTransaction Details:",
                f"- Classification: {prediction_label}",
                f"- Confidence Level: {prediction_probability:.1%}",
                "\nCould you please confirm whether this transaction was authorized by you?",
                "If you have any questions, please don't hesitate to contact your relationship manager."
            ]
        elif "Regulator" in persona_role or "FCA" in persona_role:
            # Formal regulatory fallback
            narrative_parts = [
                f"Subject transaction has been classified as {prediction_label} with {prediction_probability:.1%} confidence.",
                "\nKey Observations:"
            ]
            for i, contrib in enumerate(shap_contributors, 1):
                feature = contrib.get("feature", "Unknown")
                value = contrib.get("actual_value", 0)
                narrative_parts.append(f"{i}. {feature}: {value:.2f}")
            narrative_parts.append("\nThis activity warrants further review as part of ongoing suspicious activity monitoring.")
        else:
            # Technical/compliance fallback
            narrative_parts = [
                f"This transaction has been classified as {prediction_label} with {prediction_probability:.1%} confidence.",
                "\nKey Risk Factors:\n"
            ]
            for i, contrib in enumerate(shap_contributors, 1):
                feature = contrib.get("feature", "Unknown")
                value = contrib.get("actual_value", 0)
                shap_val = contrib.get("shap_contribution", 0)
                direction = contrib.get("direction", "unknown")
                impact = "increased" if direction == "increased" else "decreased"
                narrative_parts.append(
                    f"{i}. {feature}: Value of {value:.2f} {impact} risk by {abs(shap_val):.4f}"
                )
            narrative_parts.append("\n\nRecommended Action: This transaction requires immediate review.")
        
        return "\n".join(narrative_parts)