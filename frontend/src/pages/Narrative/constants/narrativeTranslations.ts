export const NARRATIVE_TRANSLATIONS: Record<string, Record<string, { title: string; content: string }>> = {
    en: {
        "fraud-analyst": {
            title: "AI Generated Narrative - Fraud Analyst",
            content: `The customer initiated a transfer of ₹4,75,000, which is 8 times higher than their average transaction value. The transaction is flagged due to a newly added beneficiary within 10 minutes of beneficiary registration. Additionally, the transaction originated from a device and IP address that are not associated with the customer's typical usage.\n\nBased on historical behavior and peer-group analysis, this activity significantly deviates from established patterns and may indicate account takeover or unauthorized account movement.`,
        },
        "compliance-officer": {
            title: "AI Generated Narrative - Compliance Officer",
            content: `This transaction exhibits multiple red flags consistent with potential account takeover or money laundering activity. The rapid sequence of beneficiary addition followed by a high-value transfer, combined with anomalous device and location indicators, requires immediate investigation.\n\nThe beneficiary account has been flagged in our network analysis as having connections to previously sanctioned accounts. This transaction should be held pending enhanced due diligence and customer verification.`,
        },
        "relationship-manager": {
            title: "AI Generated Narrative - Relationship Manager",
            content: `Your customer John Smith has attempted a large transaction of ₹4,75,000 to a newly added beneficiary. This is significantly higher than their usual transaction size (avg: ₹95,200).\n\nThe transaction occurred from a new device in Ahmedabad, which may be outside their normal activity pattern. It's recommended to contact the customer directly to verify this transaction's legitimacy and understand the business purpose behind this payment.`,
        },
        "operations-team": {
            title: "AI Generated Narrative - Operations Team",
            content: `Transaction TXN-983745 has been automatically held due to multiple risk triggers. The system detected velocity anomalies, device fingerprint mismatches, and beneficiary network risks.\n\nProcessing this transaction requires manual override with supervisor approval. Ensure all verification protocols are completed before releasing funds. Document all investigation steps in the case management system.`,
        },
        "executive-summary": {
            title: "Executive Summary",
            content: `High-risk transaction detected: ₹4.75L transfer from established customer using new device to recently added beneficiary with suspicious network connections. Transaction held for investigation. Recommended action: Customer verification and enhanced due diligence before fund release.`,
        },
    },
    // Add other languages (es, fr, de, hi, zh) here if needed
};
