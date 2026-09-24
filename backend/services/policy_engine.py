"""
Fraud Policy Engine.
Implements Rules R1 to R10, approval routes (auto, L1, L2),
and determines initial recommendations, simulated evidence responses,
and final recommendations.
"""

from typing import Any, Dict, List, Tuple


class PolicyEngine:
    """
    Evaluates actions and approval routes strictly according to Fraud Policy V1.0.
    """

    @staticmethod
    def get_approval_route(action: str, exposure_usd: float = 0.0) -> str:
        """
        Determines the required approval route for an action.
        """
        if action == "DECLINE_TRANSACTION":
            return "L1"

        if action == "BLOCK_CARD":
            return "L2" if exposure_usd > 2500.0 else "L1"

        if action in ("BLOCK_ALL_CARDS", "FILE_REPORT"):
            return "L2"

        return "auto"

    @classmethod
    def evaluate_initial_actions(
        cls,
        trigger_type: str,
        verdict: str,
        fraud_probability: float,
        pattern: str,
        exposure_usd: float,
        is_recurring: bool = False,
        cleared_purchase_over_100: bool = False,
        connected_cards: List[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Determine initial recommendations before requested evidence arrives.
        """
        connected_cards = connected_cards or []
        actions: List[Dict[str, str]] = []

        if is_recurring:
            # Rule R7: Disputed but legitimate recurring charge
            actions.append({
                "action": "CREATE_CASE",
                "route": cls.get_approval_route("CREATE_CASE"),
                "reason": "R7: Recurring charge pattern detected, verify prior to blocking",
            })
            actions.append({
                "action": "VERIFY_WITH_CUSTOMER",
                "route": cls.get_approval_route("VERIFY_WITH_CUSTOMER"),
                "reason": "R7: Request customer verification on recurring subscription",
            })
            actions.append({
                "action": "WARN_CUSTOMER",
                "route": cls.get_approval_route("WARN_CUSTOMER"),
                "reason": "R7: Send recurring charge alert and subscription tips",
            })
            return actions

        if pattern == "card_testing":
            # Rule R5
            actions.append({
                "action": "DECLINE_TRANSACTION",
                "route": cls.get_approval_route("DECLINE_TRANSACTION"),
                "reason": "R5: Micro-authorization testing sequence observed",
            })
            if cleared_purchase_over_100:
                actions.append({
                    "action": "BLOCK_CARD",
                    "route": cls.get_approval_route("BLOCK_CARD", exposure_usd),
                    "reason": f"R5: Subsequent testing purchase over $100 has cleared (exposure: ${exposure_usd:.2f})",
                })
            else:
                actions.append({
                    "action": "STEP_UP_AUTH",
                    "route": cls.get_approval_route("STEP_UP_AUTH"),
                    "reason": "R5: Require step-up authentication following testing sequence",
                })
            return actions

        if trigger_type == "customer_report":
            # Customer has already initiated a report/dispute
            actions.append({
                "action": "CREATE_CASE",
                "route": cls.get_approval_route("CREATE_CASE"),
                "reason": "R2: Customer reported unauthorized charge, open internal case",
            })
            actions.append({
                "action": "VERIFY_WITH_CUSTOMER",
                "route": cls.get_approval_route("VERIFY_WITH_CUSTOMER"),
                "reason": "R1 & R2: Validate transaction specifics and card possession status",
            })
            return actions

        if fraud_probability < 0.70:
            # Rule R1: Weak signal (< 0.70 probability on single signal)
            actions.append({
                "action": "VERIFY_WITH_CUSTOMER",
                "route": cls.get_approval_route("VERIFY_WITH_CUSTOMER"),
                "reason": f"R1: Assessed fraud probability {fraud_probability:.2f} < 0.70; verify before blocking",
            })
            actions.append({
                "action": "MONITOR_CARD",
                "route": cls.get_approval_route("MONITOR_CARD"),
                "reason": "R1: Raise card monitoring sensitivity pending verification",
            })
            return actions

        # Strong signal (> 0.70)
        actions.append({
            "action": "DECLINE_TRANSACTION",
            "route": cls.get_approval_route("DECLINE_TRANSACTION"),
            "reason": f"Policy 1: High fraud probability ({fraud_probability:.2f}) on flagged transaction",
        })
        actions.append({
            "action": "VERIFY_WITH_CUSTOMER",
            "route": cls.get_approval_route("VERIFY_WITH_CUSTOMER"),
            "reason": "R1: Confirm unauthorized status with cardholder before permanent block",
        })

        return actions

    @classmethod
    def evaluate_final_actions(
        cls,
        verdict: str,
        fraud_probability: float,
        pattern: str,
        exposure_usd: float,
        assumed_customer_response: str,
        connected_cards: List[str] = None,
        has_shared_device_or_ring: bool = False,
        has_compromised_credentials: bool = False,
        multiple_customer_cards_affected: bool = False,
    ) -> Tuple[List[Dict[str, str]], bool, str, str]:
        """
        Determine final actions after simulated evidence responses.
        Returns (final_actions, should_file_sar, sar_reason, what_changed).
        """
        connected_cards = connected_cards or []
        actions: List[Dict[str, str]] = []
        should_file_sar = False
        sar_reason = ""
        what_changed = ""

        if verdict == "legitimate":
            actions.append({
                "action": "CLOSE_NO_FRAUD",
                "route": cls.get_approval_route("CLOSE_NO_FRAUD"),
                "reason": "R3: Cardholder confirmed transaction validity / verified legitimate activity",
            })
            what_changed = (
                f"Customer verification confirmed legitimate activity. Alert closed as no fraud under R3."
            )
            return actions, False, "", what_changed

        if verdict == "uncertain":
            # Rule R8
            actions.append({
                "action": "CREATE_CASE",
                "route": cls.get_approval_route("CREATE_CASE"),
                "reason": "R8: Uncertain verdict with pending anomalies; record internal investigation",
            })
            actions.append({
                "action": "ESCALATE_TO_ANALYST",
                "route": cls.get_approval_route("ESCALATE_TO_ANALYST"),
                "reason": f"R8: Escalated to human analyst due to uncertain verdict and exposure (${exposure_usd:.2f})",
            })
            actions.append({
                "action": "MONITOR_CARD",
                "route": cls.get_approval_route("MONITOR_CARD"),
                "reason": "R4 & R8: Heightened surveillance on card during analyst review",
            })
            what_changed = "Evidence remained inconclusive; case escalated to fraud analyst under Rule R8."
            return actions, False, "", what_changed

        # Verdict is fraud
        # Check Rule R10: BLOCK_ALL_CARDS only if credentials compromised or >= 2 cards affected
        if multiple_customer_cards_affected or has_compromised_credentials:
            actions.append({
                "action": "BLOCK_ALL_CARDS",
                "route": cls.get_approval_route("BLOCK_ALL_CARDS"),
                "reason": "R10: Multiple cards compromised under account takeover / credential compromise",
            })
        else:
            actions.append({
                "action": "BLOCK_CARD",
                "route": cls.get_approval_route("BLOCK_CARD", exposure_usd),
                "reason": (
                    f"R2: Customer denied transaction; exposure is ${exposure_usd:.2f} "
                    f"({'exceeds $2,500' if exposure_usd > 2500.0 else 'under $2,500'})"
                ),
            })

        actions.append({
            "action": "CREATE_CASE",
            "route": cls.get_approval_route("CREATE_CASE"),
            "reason": "R2: Open internal case and persist evidence to graph",
        })

        # Evaluate SAR criteria (FinCEN / Section 3a)
        # Exposure > $1,000 OR shared origin (R6) OR undocumented pattern (R9)
        reasons_for_sar = []
        if exposure_usd > 1000.0:
            reasons_for_sar.append(f"exposure of ${exposure_usd:,.2f} exceeds $1,000 threshold")

        if has_shared_device_or_ring or connected_cards:
            reasons_for_sar.append("activity connects to shared device profile or multi-card fraud ring")

        if pattern == "undocumented":
            reasons_for_sar.append("R9: novel coordinated undocumented fraud typology")

        if reasons_for_sar:
            should_file_sar = True
            sar_reason = f"R2 & FinCEN compliance: {'; '.join(reasons_for_sar)}"
            actions.append({
                "action": "FILE_REPORT",
                "route": cls.get_approval_route("FILE_REPORT"),
                "reason": sar_reason,
            })

        if has_shared_device_or_ring or connected_cards:
            actions.append({
                "action": "MONITOR_CONNECTED_CARDS",
                "route": cls.get_approval_route("MONITOR_CONNECTED_CARDS"),
                "reason": f"R6: Monitor linked cards ({', '.join(connected_cards)}) sharing fraud origin",
            })

        if pattern == "undocumented":
            actions.append({
                "action": "ESCALATE_TO_ANALYST",
                "route": cls.get_approval_route("ESCALATE_TO_ANALYST"),
                "reason": "R9: Undocumented coordinated pattern requires analyst review",
            })

        what_changed = (
            f"Customer confirmed unauthorized activity (assumed denial). Probability elevated to {fraud_probability:.2f}. "
            f"Actions progressed from verification to immediate card block{' and regulatory SAR filing' if should_file_sar else ''}."
        )

        return actions, should_file_sar, sar_reason, what_changed
