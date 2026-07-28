import {
    FireOutlined,
    ClockCircleOutlined,
    WarningOutlined,
    ThunderboltOutlined,
    UserOutlined,
} from "@ant-design/icons";
import { RiskIndicator, RecommendedAction, TimelineEvent } from "../components";

export const LANGUAGES = [
    { value: "en", label: "English", flag: "🇬🇧", voice: "en-US" },
    { value: "es", label: "Español", flag: "🇪🇸", voice: "es-ES" },
    { value: "fr", label: "Français", flag: "🇫🇷", voice: "fr-FR" },
    { value: "de", label: "Deutsch", flag: "🇩🇪", voice: "de-DE" },
    { value: "hi", label: "हिन्दी", flag: "🇮🇳", voice: "hi-IN" },
    { value: "zh", label: "中文", flag: "🇨🇳", voice: "zh-CN" },
];

export const RISK_INDICATORS: RiskIndicator[] = [
    {
        id: "1",
        icon: <FireOutlined />,
        label: "Amount is 800% higher than normal",
        description: "Transaction amount significantly exceeds historical patterns",
        severity: "high",
    },
    {
        id: "2",
        icon: <ClockCircleOutlined />,
        label: "Beneficiary added just paid within 10 mins",
        description: "Rapid transaction after beneficiary registration",
        severity: "high",
    },
    {
        id: "3",
        icon: <WarningOutlined />,
        label: "Login from new device",
        description: "First transaction from this device",
        severity: "medium",
    },
    {
        id: "4",
        icon: <ThunderboltOutlined />,
        label: "Unusual login location",
        description: "Location differs from typical access pattern",
        severity: "medium",
    },
    {
        id: "5",
        icon: <UserOutlined />,
        label: "Beneficiary linked to flagged accounts",
        description: "Destination account has suspicious connections",
        severity: "high",
    },
];

export const RISK_CONTRIBUTION = [
    { factor: "High Amount", percentage: 45, color: "#ff4d4f" },
    { factor: "New Beneficiary", percentage: 25, color: "#ff7a45" },
    { factor: "New Device", percentage: 15, color: "#ffa940" },
    { factor: "Location", percentage: 10, color: "#ffc53d" },
    { factor: "Network Risk", percentage: 5, color: "#ffec3d" },
];

export const INVESTIGATION_TIMELINE: TimelineEvent[] = [
    {
        time: "09:05 AM",
        title: "Beneficiary added by customer",
        description: "New beneficiary XXXX9821 registered",
        type: "normal",
    },
    {
        time: "09:12 AM",
        title: "Login from new device detected",
        description: "iPhone 14 Pro from Ahmedabad (103.21.45.207)",
        type: "warning",
    },
    {
        time: "09:15 AM",
        title: "Transaction initiated for ₹4,75,000",
        description: "High-value transfer to newly added beneficiary",
        type: "error",
    },
    {
        time: "09:15 AM",
        title: "Anomaly detected and risk alert generated",
        description: "Risk score: 92/100 - Transaction held for review",
        type: "error",
    },
];

export const RECOMMENDED_ACTIONS: RecommendedAction[] = [
    {
        priority: "immediate",
        title: "Immediate (Now)",
        actions: [
            "Hold transaction",
            "Verify customer identity",
            "Validate beneficiary details",
        ],
    },
    {
        priority: "within-1-hour",
        title: "Within 1 Hour",
        actions: [
            "Review linked accounts",
            "Compare AML screening",
            "Contact customer for verification",
            "Perform device analysis",
        ],
    },
    {
        priority: "long-term",
        title: "Long Term",
        actions: [
            "Strengthen transaction limits",
            "Enable adaptive authorization",
            "Update beneficiary rules",
            "Monitor account for 30 days",
        ],
    },
];
