import unittest
from datetime import datetime, timedelta

from backend.services.config import PatternRuleConfig
from backend.services.investigation_engine import DeterministicFraudEngine


class MockGraphClient:
    def __init__(self, transactions, related_cases=None):
        self.transactions = transactions
        self.related_cases = related_cases or []

    def get_transaction(self, txn_id):
        return next(
            transaction
            for transaction in self.transactions
            if transaction["TransactionID"] == txn_id
        )

    def get_card_history(self, card_id):
        return list(self.transactions)

    def get_shared_entities(self, txn_id):
        return {
            "connected_cards": [],
            "device_profiles": [],
        }

    def get_related_cases(self, device_profiles):
        return list(self.related_cases)


class TestDeterministicEngine(unittest.TestCase):

    def make_trigger(
        self,
        txn_id="FLAG",
        card_id="C1",
        timestamp=None,
    ):
        return {
            "case_id": "TEST_CASE",
            "trigger_type": "risk_score",
            "flagged_txn_id": txn_id,
            "card_id": card_id,
            "customer_id": "TEST_CUSTOMER",
            "risk_score": 0.8,
            "timestamp": timestamp,
        }

    def test_pattern_1_blocked_when_threshold_unverified(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 2.0,
                "channel": "online",
                "ts": base,
            },
            {
                "TransactionID": "T2",
                "TransactionAmt": 3.0,
                "channel": "online",
                "ts": base + timedelta(minutes=10),
            },
            {
                "TransactionID": "T3",
                "TransactionAmt": 1.5,
                "channel": "online",
                "ts": base + timedelta(minutes=20),
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 100.0,
                "channel": "online",
                "ts": base + timedelta(minutes=30),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertNotIn(
            "card_testing",
            result.detected_patterns,
        )

        self.assertTrue(
            any(
                "threshold is unverified" in message
                for message in result.missing_evidence
            )
        )

    def test_pattern_1_triggers_with_explicit_verified_threshold(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 2.0,
                "channel": "online",
                "ts": base,
            },
            {
                "TransactionID": "T2",
                "TransactionAmt": 3.0,
                "channel": "online",
                "ts": base + timedelta(minutes=10),
            },
            {
                "TransactionID": "T3",
                "TransactionAmt": 1.5,
                "channel": "online",
                "ts": base + timedelta(minutes=20),
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 100.0,
                "channel": "online",
                "ts": base + timedelta(minutes=30),
            },
        ]

        config = PatternRuleConfig(
            P1_SMALL_AUTH_THRESHOLD=5.0
        )

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions),
            config=config,
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertIn(
            "card_testing",
            result.detected_patterns,
        )

        self.assertEqual(
            result.exposure_usd,
            106.5,
        )

    def test_pattern_1_insufficient_authorizations(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 2.0,
                "channel": "online",
                "ts": base,
            },
            {
                "TransactionID": "T2",
                "TransactionAmt": 3.0,
                "channel": "online",
                "ts": base + timedelta(minutes=10),
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 100.0,
                "channel": "online",
                "ts": base + timedelta(minutes=30),
            },
        ]

        config = PatternRuleConfig(
            P1_SMALL_AUTH_THRESHOLD=5.0
        )

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions),
            config=config,
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertNotIn(
            "card_testing",
            result.detected_patterns,
        )

    def test_pattern_2_lower_boundary(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base,
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=1),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertTrue(
            result.risk_indicators.is_velocity_spike
        )

    def test_pattern_2_upper_boundary(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": f"T{i}",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=i),
            }
            for i in range(3)
        ]

        transactions.append(
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=4),
            }
        )

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertTrue(
            result.risk_indicators.is_velocity_spike
        )

    def test_pattern_2_outside_range(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": f"T{i}",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=i),
            }
            for i in range(4)
        ]

        transactions.append(
            {
                "TransactionID": "T4",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=4),
            }
        )

        transactions.append(
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 50.0,
                "channel": "online",
                "ts": base + timedelta(hours=5),
            }
        )

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertFalse(
            any(
                evidence.rule_id == "Pattern_2"
                for evidence in result.evidence
            )
        )

    def test_pattern_3_requires_pattern_2(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 50.0,
                "channel": "online",
                "id_15": "New",
                "ts": base,
            }
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertNotIn(
            "card_not_present_new_device",
            result.detected_patterns,
        )

    def test_pattern_3_requires_new_device(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 50.0,
                "channel": "online",
                "id_15": "Known",
                "ts": base,
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 50.0,
                "channel": "online",
                "id_15": "Known",
                "ts": base + timedelta(hours=1),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertNotIn(
            "card_not_present_new_device",
            result.detected_patterns,
        )

    def test_pattern_4_is_partial(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 100.0,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "87",
                "ts": base,
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 200.0,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "315",
                "ts": base + timedelta(days=2),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertIn(
            "out_of_region_use_partial",
            result.detected_patterns,
        )

        self.assertTrue(
            any(
                "normal cardholder activity" in message
                for message in result.missing_evidence
            )
        )

    def test_pattern_5_unverified_timeframe_does_not_trigger(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 100.0,
                "channel": "in_person",
                "ts": base,
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 200.0,
                "channel": "online",
                "id_15": "New",
                "ts": base + timedelta(hours=1),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertNotIn(
            "account_takeover_partial",
            result.detected_patterns,
        )

        self.assertTrue(
            any(
                "timeframe is unverified" in message
                for message in result.missing_evidence
            )
        )

    def test_related_and_similar_cases_are_separate(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 100.0,
                "channel": "online",
                "ts": base,
            }
        ]

        related_cases = [
            {
                "case_id": "CASE_001",
                "outcome": "confirmed_fraud",
            }
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(
                transactions,
                related_cases=related_cases,
            )
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertEqual(
            result.related_cases,
            ["CASE_001"],
        )

        self.assertEqual(
            result.similar_cases,
            [],
        )

        self.assertEqual(
            result.risk_indicators.hard_linked_fraud_cases,
            1,
        )

    def test_exposure_only_uses_affected_transactions(self):
        base = datetime(2026, 1, 1, 10, 0)

        transactions = [
            {
                "TransactionID": "T1",
                "TransactionAmt": 10.0,
                "channel": "online",
                "ts": base,
            },
            {
                "TransactionID": "FLAG",
                "TransactionAmt": 100.0,
                "channel": "online",
                "ts": base + timedelta(hours=1),
            },
            {
                "TransactionID": "UNRELATED",
                "TransactionAmt": 9999.0,
                "channel": "online",
                "ts": base + timedelta(hours=2),
            },
        ]

        engine = DeterministicFraudEngine(
            MockGraphClient(transactions)
        )

        result = engine.investigate(
            self.make_trigger()
        )

        self.assertEqual(
            result.exposure_usd,
            100.0,
        )


if __name__ == "__main__":
    unittest.main()