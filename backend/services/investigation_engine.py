import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from backend.services.config import PatternRuleConfig


class EvidenceItem(BaseModel):
    evidence_id: str
    claim: str
    source_type: str
    source_ref: str
    entity_ids: List[str] = Field(default_factory=list)
    transaction_ids: List[str] = Field(default_factory=list)
    rule_id: Optional[str] = None
    calculation: Optional[str] = None
    timestamp: str


class RiskIndicators(BaseModel):
    source_risk_score: float = 0.0
    is_velocity_spike: bool = False
    is_new_device: bool = False
    is_new_region: bool = False
    is_mixed_channel: bool = False
    hard_linked_fraud_cases: int = 0


class InvestigationResult(BaseModel):
    case_id: str
    trigger_type: str
    flagged_txn_id: str
    customer_id: str
    card_id: str

    affected_txn_ids: Set[str] = Field(default_factory=set)
    connected_card_ids: Set[str] = Field(default_factory=set)
    connected_device_profiles: Set[str] = Field(default_factory=set)

    detected_patterns: List[str] = Field(default_factory=list)
    risk_indicators: RiskIndicators
    evidence: List[EvidenceItem] = Field(default_factory=list)

    related_cases: List[str] = Field(default_factory=list)
    similar_cases: List[str] = Field(default_factory=list)

    exposure_usd: float = 0.0

    uncertainty_factors: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)

    investigation_status: str = "open"


class DeterministicFraudEngine:
    """
    Deterministic fact-gathering and rule-evaluation engine.

    This class does not make probabilistic fraud predictions.
    It gathers evidence, evaluates explicitly configured rules,
    and records uncertainty when evidence is insufficient.
    """

    def __init__(
        self,
        graph_client: Any,
        config: Optional[PatternRuleConfig] = None,
    ):
        self.graph = graph_client
        self.config = config if config is not None else PatternRuleConfig()

    @staticmethod
    def _evidence_id() -> str:
        return uuid.uuid4().hex[:12]

    @staticmethod
    def _timestamp(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()

        if value is None:
            return "unknown"

        return str(value)

    @staticmethod
    def _transaction_time(transaction: Dict[str, Any]) -> Optional[datetime]:
        value = transaction.get("ts")

        if isinstance(value, datetime):
            return value

        return None

    @staticmethod
    def _transaction_id(transaction: Dict[str, Any]) -> Optional[str]:
        value = transaction.get("TransactionID")

        if value is None:
            return None

        return str(value)

    def investigate(self, trigger: Dict[str, Any]) -> InvestigationResult:
        flagged_txn_id = str(trigger["flagged_txn_id"])

        flagged_txn = self.graph.get_transaction(flagged_txn_id)

        if not flagged_txn:
            raise ValueError(
                f"Transaction '{flagged_txn_id}' was not found by the graph client."
            )

        card_id = str(trigger["card_id"])

        history = self.graph.get_card_history(card_id) or []

        shared_entities = (
            self.graph.get_shared_entities(flagged_txn_id) or {}
        )

        related_cases = self.graph.get_related_cases(
            shared_entities.get("device_profiles", [])
        ) or []

        raw_risk_score = trigger.get("risk_score", 0.0)
        try:
            source_risk = float(raw_risk_score) if raw_risk_score not in (None, "") else 0.0
        except (ValueError, TypeError):
            source_risk = 0.0

        result = InvestigationResult(
            case_id=str(trigger["case_id"]),
            trigger_type=str(trigger.get("trigger_type", "risk_score")),
            flagged_txn_id=flagged_txn_id,
            customer_id=str(trigger["customer_id"]),
            card_id=card_id,
            risk_indicators=RiskIndicators(
                source_risk_score=source_risk,
                hard_linked_fraud_cases=self._count_confirmed_fraud_cases(
                    related_cases
                ),
            ),
        )

        result.affected_txn_ids.add(flagged_txn_id)

        result.connected_card_ids.update(
            str(value)
            for value in shared_entities.get("connected_cards", [])
            if value is not None
        )

        result.connected_device_profiles.update(
            str(value)
            for value in shared_entities.get("device_profiles", [])
            if value is not None
        )

        result.related_cases = self._extract_case_ids(related_cases)

        # Similar-case retrieval is intentionally not fabricated.
        # It will be implemented later through TigerGraph/GraphRAG.
        result.similar_cases = []

        if not result.related_cases:
            result.uncertainty_factors.append(
                "No graph-connected historical fraud cases were found."
            )

        self._detect_pattern_1(
            history=history,
            flagged=flagged_txn,
            result=result,
        )

        p2_triggered = self._detect_pattern_2(
            history=history,
            flagged=flagged_txn,
            result=result,
        )

        self._detect_pattern_3(
            flagged=flagged_txn,
            p2_triggered=p2_triggered,
            result=result,
        )

        self._detect_pattern_4(
            history=history,
            flagged=flagged_txn,
            result=result,
        )

        self._detect_pattern_5(
            history=history,
            flagged=flagged_txn,
            result=result,
        )

        self._calculate_exposure(
            history=history,
            result=result,
        )

        return result

    @staticmethod
    def _extract_case_ids(related_cases: List[Any]) -> List[str]:
        case_ids: List[str] = []

        for case in related_cases:
            if isinstance(case, dict):
                case_id = case.get("case_id")
            else:
                case_id = None

            if case_id is not None:
                case_ids.append(str(case_id))

        return case_ids

    @staticmethod
    def _count_confirmed_fraud_cases(
        related_cases: List[Any],
    ) -> int:
        count = 0

        for case in related_cases:
            if not isinstance(case, dict):
                continue

            outcome = str(case.get("outcome", "")).lower()

            if outcome == "confirmed_fraud":
                count += 1

        return count

    def _add_missing_evidence(
        self,
        result: InvestigationResult,
        message: str,
    ) -> None:
        if message not in result.missing_evidence:
            result.missing_evidence.append(message)

    def _add_uncertainty(
        self,
        result: InvestigationResult,
        message: str,
    ) -> None:
        if message not in result.uncertainty_factors:
            result.uncertainty_factors.append(message)

    def _add_evidence(
        self,
        result: InvestigationResult,
        *,
        claim: str,
        source_type: str,
        source_ref: str,
        entity_ids: Optional[List[str]] = None,
        transaction_ids: Optional[List[str]] = None,
        rule_id: Optional[str] = None,
        calculation: Optional[str] = None,
        timestamp: Any = None,
    ) -> None:
        result.evidence.append(
            EvidenceItem(
                evidence_id=self._evidence_id(),
                claim=claim,
                source_type=source_type,
                source_ref=source_ref,
                entity_ids=entity_ids or [],
                transaction_ids=transaction_ids or [],
                rule_id=rule_id,
                calculation=calculation,
                timestamp=self._timestamp(timestamp),
            )
        )

    def _detect_pattern_1(
        self,
        history: List[Dict[str, Any]],
        flagged: Dict[str, Any],
        result: InvestigationResult,
    ) -> None:
        """
        Pattern 1: card-testing sequence.

        The exact small-authorization dollar threshold is currently
        unverified. Therefore the detector cannot claim the pattern
        without an explicitly supplied threshold.
        """

        if flagged.get("channel") != "online":
            return

        threshold = self.config.P1_SMALL_AUTH_THRESHOLD

        if threshold is None:
            self._add_missing_evidence(
                result,
                "Pattern 1 cannot be fully evaluated because the "
                "small-authorization dollar threshold is unverified.",
            )

            self._add_uncertainty(
                result,
                "Pattern 1 threshold is not verified from the authoritative source.",
            )

            return

        flagged_time = self._transaction_time(flagged)

        if flagged_time is None:
            self._add_missing_evidence(
                result,
                "Pattern 1 requires a valid timestamp for the flagged transaction.",
            )
            return

        prior_txns: List[Dict[str, Any]] = []

        for transaction in history:
            transaction_id = self._transaction_id(transaction)
            transaction_time = self._transaction_time(transaction)

            if transaction_id is None or transaction_time is None:
                continue

            if transaction_id == self._transaction_id(flagged):
                continue

            if transaction_time >= flagged_time:
                continue

            if (
                flagged_time - transaction_time
                > timedelta(hours=self.config.P1_TIME_WINDOW_HOURS)
            ):
                continue

            prior_txns.append(transaction)

        small_auths = [
            transaction
            for transaction in prior_txns
            if transaction.get("channel") == "online"
            and self._safe_amount(transaction) is not None
            and self._safe_amount(transaction) <= threshold
        ]

        if len(small_auths) < self.config.P1_MIN_AUTHS:
            return

        flagged_amount = self._safe_amount(flagged)

        if flagged_amount is None:
            self._add_missing_evidence(
                result,
                "Pattern 1 requires a valid TransactionAmt for the flagged transaction.",
            )
            return

        max_small = max(
            self._safe_amount(transaction)
            for transaction in small_auths
        )

        if flagged_amount <= max_small:
            return

        transaction_ids = [
            self._transaction_id(transaction)
            for transaction in small_auths
        ]

        transaction_ids = [
            transaction_id
            for transaction_id in transaction_ids
            if transaction_id is not None
        ]

        result.detected_patterns.append("card_testing")
        result.risk_indicators.is_velocity_spike = True
        result.affected_txn_ids.update(transaction_ids)

        self._add_evidence(
            result,
            claim=(
                f"{len(small_auths)} online authorizations at or below "
                f"${threshold:.2f} occurred within "
                f"{self.config.P1_TIME_WINDOW_HOURS} hour(s) before "
                f"a larger online transaction."
            ),
            source_type="deterministic_calculation",
            source_ref="pattern:card_testing",
            entity_ids=[result.card_id],
            transaction_ids=transaction_ids + [result.flagged_txn_id],
            rule_id="Pattern_1",
            calculation=(
                f"count={len(small_auths)} >= "
                f"{self.config.P1_MIN_AUTHS}; "
                f"flagged_amount={flagged_amount}; "
                f"max_small_amount={max_small}"
            ),
            timestamp=flagged.get("ts"),
        )

    def _detect_pattern_2(
        self,
        history: List[Dict[str, Any]],
        flagged: Dict[str, Any],
        result: InvestigationResult,
    ) -> bool:
        """
        Pattern 2 is treated as a deterministic velocity indicator,
        not as proof of fraud.
        """

        if flagged.get("channel") != "online":
            return False

        flagged_time = self._transaction_time(flagged)

        if flagged_time is None:
            self._add_missing_evidence(
                result,
                "Pattern 2 requires a valid timestamp.",
            )
            return False

        window_start = flagged_time - timedelta(
            hours=self.config.P2_TIME_WINDOW_HOURS
        )

        burst: List[Dict[str, Any]] = []

        for transaction in history:
            transaction_time = self._transaction_time(transaction)

            if transaction_time is None:
                continue

            if not (
                window_start
                <= transaction_time
                <= flagged_time
            ):
                continue

            if transaction.get("channel") == "online":
                burst.append(transaction)

        burst_count = len(burst)

        if not (
            self.config.P2_BURST_MIN
            <= burst_count
            <= self.config.P2_BURST_MAX
        ):
            return False

        result.risk_indicators.is_velocity_spike = True

        transaction_ids = [
            self._transaction_id(transaction)
            for transaction in burst
        ]

        transaction_ids = [
            transaction_id
            for transaction_id in transaction_ids
            if transaction_id is not None
        ]

        

        self._add_missing_evidence(
            result,
            "Pattern 2 velocity is present, but behavioral analysis is required "
            "to determine whether transaction amounts and products fit normal "
            "cardholder history.",
        )

        self._add_evidence(
            result,
            claim=(
                f"{burst_count} online transactions occurred within "
                f"{self.config.P2_TIME_WINDOW_HOURS} hours of the flagged "
                f"transaction, within the configured velocity range."
            ),
            source_type="deterministic_calculation",
            source_ref="pattern:cnp_velocity",
            entity_ids=[result.card_id],
            transaction_ids=transaction_ids,
            rule_id="Pattern_2",
            calculation=(
                f"burst_count={burst_count}; "
                f"allowed_range="
                f"{self.config.P2_BURST_MIN}-"
                f"{self.config.P2_BURST_MAX}"
            ),
            timestamp=flagged.get("ts"),
        )

        return True

    def _detect_pattern_3(
        self,
        flagged: Dict[str, Any],
        p2_triggered: bool,
        result: InvestigationResult,
    ) -> None:
        """
        Pattern 3 requires Pattern 2 plus a new-device indicator.
        """

        if not p2_triggered:
            return

        if flagged.get("id_15") != "New":
            self._add_missing_evidence(
                result,
                "Pattern 3 requires the flagged transaction's device/identity "
                "record to be marked 'New'.",
            )
            return

        result.detected_patterns.append(
            "card_not_present_new_device"
        )

        result.risk_indicators.is_new_device = True

        self._add_evidence(
            result,
            claim=(
                "The Pattern 2 velocity condition is accompanied by an "
                "identity/device record marked 'New'."
            ),
            source_type="transaction_record",
            source_ref="field:id_15",
            entity_ids=[result.card_id],
            transaction_ids=[result.flagged_txn_id],
            rule_id="Pattern_3",
            calculation="Pattern_2=True AND id_15='New'",
            timestamp=flagged.get("ts"),
        )

    def _detect_pattern_4(
        self,
        history: List[Dict[str, Any]],
        flagged: Dict[str, Any],
        result: InvestigationResult,
    ) -> None:
        """
        Pattern 4 is only reported as partial.

        A new observed region can be established from transaction history,
        but simultaneous normal activity in the historical/home region
        requires additional evidence.
        """

        if flagged.get("ProductCD") != "W":
            return

        flagged_region = flagged.get("addr1")

        if not flagged_region:
            return

        flagged_time = self._transaction_time(flagged)

        if flagged_time is None:
            self._add_missing_evidence(
                result,
                "Pattern 4 requires a valid timestamp.",
            )
            return

        prior_regions = {
            transaction.get("addr1")
            for transaction in history
            if self._transaction_time(transaction) is not None
            and self._transaction_time(transaction) < flagged_time
            and transaction.get("ProductCD") == "W"
            and transaction.get("addr1")
        }

        if not prior_regions:
            self._add_uncertainty(
                result,
                "No prior card-present region history is available.",
            )
            return

        if flagged_region in prior_regions:
            return

        result.detected_patterns.append(
            "out_of_region_use_partial"
        )

        result.risk_indicators.is_new_region = True

        self._add_missing_evidence(
            result,
            "Pattern 4 requires evidence that normal cardholder activity "
            "continues in the historical/home region during the relevant period.",
        )

        self._add_evidence(
            result,
            claim=(
                f"Card-present activity occurred in region {flagged_region}, "
                "which was not present in the card's prior observed "
                "card-present region history."
            ),
            source_type="deterministic_calculation",
            source_ref="pattern:out_of_region",
            entity_ids=[result.card_id],
            transaction_ids=[result.flagged_txn_id],
            rule_id="Pattern_4",
            calculation=(
                f"flagged_region={flagged_region}; "
                f"prior_regions={sorted(str(x) for x in prior_regions)}"
            ),
            timestamp=flagged.get("ts"),
        )

    def _detect_pattern_5(
        self,
        history: List[Dict[str, Any]],
        flagged: Dict[str, Any],
        result: InvestigationResult,
    ) -> None:
        """
        Pattern 5 remains partial until the authoritative timeframe and
        M1-M9 semantics are verified.
        """

        timeframe = self.config.P5_MIXED_CHANNEL_HOURS

        if timeframe is None:
            self._add_missing_evidence(
                result,
                "Pattern 5 cannot be fully evaluated because its "
                "mixed-channel timeframe is unverified.",
            )

            self._add_uncertainty(
                result,
                "Pattern 5 timeframe and M1-M9 anomaly definitions require verification.",
            )

            return

        flagged_time = self._transaction_time(flagged)

        if flagged_time is None:
            self._add_missing_evidence(
                result,
                "Pattern 5 requires a valid timestamp.",
            )
            return

        window_start = flagged_time - timedelta(hours=timeframe)

        recent = [
            transaction
            for transaction in history
            if (
                self._transaction_time(transaction) is not None
                and window_start
                <= self._transaction_time(transaction)
                <= flagged_time
            )
        ]

        channels = {
            transaction.get("channel")
            for transaction in recent
            if transaction.get("channel")
        }

        has_mixed_channels = len(channels) > 1
        has_new_device = flagged.get("id_15") == "New"

        if not (has_mixed_channels and has_new_device):
            return

        result.detected_patterns.append(
            "account_takeover_partial"
        )

        result.risk_indicators.is_mixed_channel = True
        result.risk_indicators.is_new_device = True

        transaction_ids = [
            self._transaction_id(transaction)
            for transaction in recent
        ]

        transaction_ids = [
            transaction_id
            for transaction_id in transaction_ids
            if transaction_id is not None
        ]

        result.affected_txn_ids.update(transaction_ids)

        self._add_missing_evidence(
            result,
            "Pattern 5 is only partial: the required M1-M9 match/anomaly "
            "conditions must be verified before treating this as a complete "
            "account-takeover pattern.",
        )

        self._add_evidence(
            result,
            claim=(
                f"Mixed-channel activity ({', '.join(sorted(channels))}) "
                "was observed together with a transaction marked as using "
                "a new device/identity."
            ),
            source_type="deterministic_calculation",
            source_ref="pattern:account_takeover",
            entity_ids=[result.card_id],
            transaction_ids=transaction_ids,
            rule_id="Pattern_5",
            calculation=(
                f"mixed_channels={sorted(channels)}; "
                f"new_device={has_new_device}"
            ),
            timestamp=flagged.get("ts"),
        )

    @staticmethod
    def _safe_amount(transaction: Dict[str, Any]) -> Optional[float]:
        try:
            value = transaction.get("TransactionAmt")

            if value is None:
                return None

            return float(value)
        except (TypeError, ValueError):
            return None

    def _calculate_exposure(
        self,
        history: List[Dict[str, Any]],
        result: InvestigationResult,
    ) -> None:
        transactions_by_id = {}

        for transaction in history:
            transaction_id = self._transaction_id(transaction)

            if transaction_id is not None:
                transactions_by_id[transaction_id] = transaction

        exposure = 0.0

        for transaction_id in result.affected_txn_ids:
            transaction = transactions_by_id.get(transaction_id)

            if transaction is None:
                self._add_missing_evidence(
                    result,
                    f"Transaction {transaction_id} is referenced by the "
                    "investigation but was not present in retrieved history.",
                )
                continue

            amount = self._safe_amount(transaction)

            if amount is None:
                self._add_missing_evidence(
                    result,
                    f"Transaction {transaction_id} has no valid TransactionAmt.",
                )
                continue

            exposure += abs(amount)

        result.exposure_usd = exposure