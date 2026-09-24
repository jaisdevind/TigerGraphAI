"""
FinCEN-compliant Suspicious Activity Report (SAR) narrative generator.
Produces structured narratives following FinCEN Narrative Guidance:
Who, What, When, Where, How, and Why the activity is suspicious (6-12 sentences).
"""

from typing import Any, Dict, List, Optional


class SARGenerator:
    """
    Generates regulatory SAR filings adhering to FinCEN standards.
    """

    @staticmethod
    def generate_narrative(
        case_id: str,
        customer_id: str,
        card_id: str,
        pattern: str,
        total_amount_usd: float,
        activity_dates: List[str],
        connected_cards: List[str],
        connected_device_profiles: List[str],
        reason: str,
        evidence_summary: str,
    ) -> str:
        date_str = (
            f"on {activity_dates[0]}"
            if len(activity_dates) == 1 or activity_dates[0] == activity_dates[1]
            else f"between {activity_dates[0]} and {activity_dates[1]}"
        )

        device_desc = (
            f" utilizing device profile ({connected_device_profiles[0]})"
            if connected_device_profiles
            else ""
        )

        connected_cards_desc = (
            f" Further graph analysis linked this activity to connected card(s) {', '.join(connected_cards)}."
            if connected_cards
            else ""
        )

        narrative_parts = [
            f"This Suspicious Activity Report ({case_id}) is filed regarding confirmed and unauthorized financial activity involving customer {customer_id} and card {card_id} {date_str}.",
            f"The flagged activity constitutes a documented '{pattern}' typology resulting in aggregate fraudulent exposure of ${total_amount_usd:,.2f} USD.",
            f"Specifically, transactions were conducted in the online channel{device_desc}, exhibiting distinct behavioral anomalies and velocity characteristics inconsistent with the established cardholder baseline.",
            f"{evidence_summary.strip()}",
            f"{connected_cards_desc}",
            f"The cardholder, upon contact by fraud operations, explicitly denied authorizing these transactions and remained in possession of the card.",
            f"Filing is mandated under Bank Fraud Policy based on {reason}, as well as FinCEN regulations governing unauthorized card compromise, coordinated payment fraud, and account takeover.",
            f"Remedial actions taken include immediate card blocking with reissue, placement of associated entities and connected cards under heightened surveillance, and internal case recording for pattern tracking.",
        ]

        # Combine into cohesive narrative (6-8 sentences meeting 6-12 FinCEN standard)
        return " ".join([part for part in narrative_parts if part])
