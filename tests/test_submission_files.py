import json
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = PROJECT_ROOT / "cases"


class TestSubmissionCases(unittest.TestCase):
    def test_all_20_cases_exist_and_conform(self):
        self.assertTrue(CASES_DIR.exists(), "cases/ directory does not exist")

        expected_case_ids = [f"HHG-{i:03d}" for i in range(1, 21)]
        found_files = list(CASES_DIR.glob("HHG-*.json"))
        self.assertEqual(len(found_files), 20, f"Expected 20 case files, found {len(found_files)}")

        legit_count = 0
        fraud_count = 0
        sar_count = 0

        for case_id in expected_case_ids:
            case_file = CASES_DIR / f"{case_id}.json"
            self.assertTrue(case_file.exists(), f"Missing file {case_file.name}")

            with open(case_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Top level checks
            self.assertEqual(data["case_id"], case_id)
            self.assertIn("case", data)
            self.assertIn("evidence_requests", data)
            self.assertIn("next_best_actions", data)
            self.assertIn("sar", data)
            self.assertIn("stop_reason", data)
            self.assertIn("tool_calls", data)
            self.assertIn("tokens", data)
            self.assertIn("latency_s", data)

            case = data["case"]
            self.assertIn(case["status"], ("open", "closed_fraud", "closed_legitimate", "escalated"))
            self.assertIn(case["verdict"], ("fraud", "legitimate", "uncertain"))
            self.assertGreaterEqual(case["fraud_probability"], 0.0)
            self.assertLessEqual(case["fraud_probability"], 1.0)
            self.assertIn(
                case["pattern"],
                (
                    "card_testing",
                    "card_not_present_fraud",
                    "card_not_present_new_device",
                    "out_of_region_use",
                    "account_takeover",
                    "undocumented",
                    "none",
                ),
            )
            self.assertTrue(case["written_to_graph"])
            self.assertTrue(case["graph_case_id"].startswith("TG-CASE-"))

            # Next best actions checks
            nba = data["next_best_actions"]
            self.assertIsInstance(nba["initial"], list)
            self.assertIsInstance(nba["final"], list)
            self.assertIn("what_changed", nba)

            for act in nba["initial"] + nba["final"]:
                self.assertIn("action", act)
                self.assertIn(act["route"], ("auto", "L1", "L2"))
                self.assertIn("reason", act)

            # SAR checks
            sar = data["sar"]
            self.assertIn("file", sar)
            self.assertIn("reason", sar)

            if sar["file"]:
                sar_count += 1
                self.assertGreater(len(sar["narrative"]), 100)
                self.assertGreater(len(sar["subjects"]), 0)
                self.assertGreater(sar["total_amount_usd"], 0)
                self.assertEqual(len(sar["activity_dates"]), 2)
            else:
                self.assertEqual(sar["narrative"], "")
                self.assertEqual(sar["subjects"], [])
                self.assertEqual(sar["total_amount_usd"], 0)
                self.assertEqual(sar["activity_dates"], [])

            if case["verdict"] == "legitimate":
                legit_count += 1
                self.assertEqual(case["affected_txn_ids"], [])
                self.assertEqual(case["exposure_usd"], 0.0)
                self.assertFalse(sar["file"])
            elif case["verdict"] == "fraud":
                fraud_count += 1
                self.assertGreater(len(case["affected_txn_ids"]), 0)
                self.assertGreater(case["exposure_usd"], 0.0)

        # 50% legitimate benchmark check
        self.assertEqual(legit_count, 10, "Expected exactly 10 legitimate cases")
        self.assertEqual(fraud_count, 10, "Expected exactly 10 fraud cases")
        self.assertGreaterEqual(sar_count, 4, "Expected at least 4 SAR reports filed")


if __name__ == "__main__":
    unittest.main()
