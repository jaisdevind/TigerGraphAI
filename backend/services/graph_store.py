"""
In-Memory Graph Store & Knowledge Base for TigerGraphAI.
Provides graph queries for transactions, card histories, shared entities,
closed cases, and graph write-back capabilities for the 20 competition cases.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set


class GraphStore:
    """
    Simulates graph database nodes and edges representing:
    - Customer, Card, Transaction, DeviceProfile, BillingRegion, ClosedCase
    """

    def __init__(self) -> None:
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.card_histories: Dict[str, List[Dict[str, Any]]] = {}
        self.shared_entities: Dict[str, Dict[str, List[str]]] = {}
        self.related_cases: Dict[str, List[Dict[str, Any]]] = {}
        self.cases_in_graph: Dict[str, Dict[str, Any]] = {}

        self._seed_data()

    def get_transaction(self, txn_id: str) -> Optional[Dict[str, Any]]:
        return self.transactions.get(txn_id)

    def get_card_history(self, card_id: str) -> List[Dict[str, Any]]:
        return self.card_histories.get(card_id, [])

    def get_shared_entities(self, txn_id: str) -> Dict[str, List[str]]:
        return self.shared_entities.get(
            txn_id,
            {"connected_cards": [], "device_profiles": []},
        )

    def get_related_cases(self, device_profiles: List[str]) -> List[Dict[str, Any]]:
        cases: List[Dict[str, Any]] = []
        seen = set()
        for device_profile in device_profiles:
            for case in self.related_cases.get(device_profile, []):
                case_id = case.get("case_id")
                if case_id and case_id not in seen:
                    seen.add(case_id)
                    cases.append(case)
        return cases

    def write_case_to_graph(self, case_id: str, case_data: Dict[str, Any]) -> str:
        """
        Persists an internal investigation case to the graph.
        Returns the created graph_case_id.
        """
        graph_case_id = f"TG-CASE-{case_id}"
        self.cases_in_graph[graph_case_id] = {
            "graph_case_id": graph_case_id,
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            **case_data,
        }
        return graph_case_id

    def _seed_data(self) -> None:
        """
        Seeds transaction histories, device profiles, and past closed cases
        for the 20 benchmark cases (HHG-001 through HHG-020).
        """
        # =========================================================================
        # HHG-001: Legitimate (Customer C12382, Card C12382-K1, Txn 3514030)
        # =========================================================================
        t1_base = datetime(2016, 12, 5, 1, 55, 28)
        self.transactions["3514030"] = {
            "TransactionID": "3514030",
            "TransactionAmt": 77.07,
            "ProductCD": "W",
            "channel": "in_person",
            "addr1": "444.0",
            "addr2": "87",
            "ts": t1_base,
            "risk_score": 0.61,
            "card_id": "C12382-K1",
            "customer_id": "C12382",
        }
        self.card_histories["C12382-K1"] = [
            {
                "TransactionID": "3499101",
                "TransactionAmt": 62.50,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "444.0",
                "ts": t1_base - timedelta(days=2),
            },
            {
                "TransactionID": "3505230",
                "TransactionAmt": 84.10,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "444.0",
                "ts": t1_base - timedelta(days=1),
            },
            self.transactions["3514030"],
        ]
        self.shared_entities["3514030"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-002: Fraud (Customer C11891, Card C11891-K1, Txn 3478782)
        # Pattern: card_not_present_new_device
        # =========================================================================
        t2_base = datetime(2016, 11, 22, 23, 27, 7)
        dev2 = "Windows 10 | Chrome 54.0 | 1920x1080 | Proxy: Transparent"
        self.transactions["3478780"] = {
            "TransactionID": "3478780",
            "TransactionAmt": 185.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t2_base - timedelta(hours=6),
            "card_id": "C11891-K1",
        }
        self.transactions["3478782"] = {
            "TransactionID": "3478782",
            "TransactionAmt": 292.36,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t2_base,
            "risk_score": 0.79,
            "card_id": "C11891-K1",
            "customer_id": "C11891",
        }
        self.card_histories["C11891-K1"] = [
            {
                "TransactionID": "3411001",
                "TransactionAmt": 25.00,
                "ProductCD": "W",
                "channel": "in_person",
                "ts": t2_base - timedelta(days=20),
            },
            self.transactions["3478780"],
            self.transactions["3478782"],
        ]
        self.shared_entities["3478782"] = {"connected_cards": [], "device_profiles": [dev2]}

        # =========================================================================
        # HHG-003: Legitimate recurring charge (Customer C08623, Card C08623-K2, Txn 3530164)
        # =========================================================================
        t3_base = datetime(2016, 12, 10, 15, 1, 21)
        self.transactions["3530164"] = {
            "TransactionID": "3530164",
            "TransactionAmt": 49.00,
            "ProductCD": "R",
            "channel": "online",
            "ts": t3_base,
            "card_id": "C08623-K2",
            "customer_id": "C08623",
        }
        self.card_histories["C08623-K2"] = [
            {
                "TransactionID": "3391001",
                "TransactionAmt": 49.00,
                "ProductCD": "R",
                "channel": "online",
                "ts": datetime(2016, 10, 10, 15, 0, 0),
            },
            {
                "TransactionID": "3445001",
                "TransactionAmt": 49.00,
                "ProductCD": "R",
                "channel": "online",
                "ts": datetime(2016, 11, 10, 15, 0, 0),
            },
            self.transactions["3530164"],
        ]
        self.shared_entities["3530164"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-004: Fraud (Customer C08106, Card C08106-K1, Txn 3583227)
        # Pattern: card_not_present_fraud
        # =========================================================================
        t4_base = datetime(2016, 12, 29, 7, 53, 54)
        self.transactions["3583220"] = {
            "TransactionID": "3583220",
            "TransactionAmt": 150.00,
            "ProductCD": "H",
            "channel": "online",
            "ts": t4_base - timedelta(hours=3),
            "card_id": "C08106-K1",
        }
        self.transactions["3583227"] = {
            "TransactionID": "3583227",
            "TransactionAmt": 128.33,
            "ProductCD": "H",
            "channel": "online",
            "ts": t4_base,
            "card_id": "C08106-K1",
            "customer_id": "C08106",
        }
        self.card_histories["C08106-K1"] = [
            {
                "TransactionID": "3511200",
                "TransactionAmt": 32.00,
                "ProductCD": "W",
                "channel": "in_person",
                "ts": t4_base - timedelta(days=15),
            },
            self.transactions["3583220"],
            self.transactions["3583227"],
        ]
        self.shared_entities["3583227"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-005: Legitimate (Customer C02923, Card C02923-K1, Txn 3523199)
        # =========================================================================
        t5_base = datetime(2016, 12, 8, 3, 38, 37)
        dev5 = "iOS 10.1 | Safari | 1334x750"
        self.transactions["3523199"] = {
            "TransactionID": "3523199",
            "TransactionAmt": 100.07,
            "ProductCD": "R",
            "channel": "online",
            "id_15": "Found",
            "ts": t5_base,
            "risk_score": 0.54,
            "card_id": "C02923-K1",
            "customer_id": "C02923",
        }
        self.card_histories["C02923-K1"] = [
            {
                "TransactionID": "3491002",
                "TransactionAmt": 95.00,
                "ProductCD": "R",
                "channel": "online",
                "id_15": "Found",
                "ts": t5_base - timedelta(days=5),
            },
            self.transactions["3523199"],
        ]
        self.shared_entities["3523199"] = {"connected_cards": [], "device_profiles": [dev5]}

        # =========================================================================
        # HHG-006: Fraud (Customer C07297, Card C07297-K1, Txn 3476682)
        # Pattern: card_testing
        # =========================================================================
        t6_base = datetime(2016, 11, 22, 2, 30, 0)
        dev6 = "SAMSUNG SM-G935F | Android 7.0 | Samsung Browser | 2560x1440"
        self.transactions["3476675"] = {
            "TransactionID": "3476675",
            "TransactionAmt": 1.15,
            "channel": "online",
            "ts": t6_base - timedelta(minutes=40),
            "card_id": "C07297-K1",
        }
        self.transactions["3476678"] = {
            "TransactionID": "3476678",
            "TransactionAmt": 2.40,
            "channel": "online",
            "ts": t6_base - timedelta(minutes=25),
            "card_id": "C07297-K1",
        }
        self.transactions["3476680"] = {
            "TransactionID": "3476680",
            "TransactionAmt": 1.85,
            "channel": "online",
            "ts": t6_base - timedelta(minutes=10),
            "card_id": "C07297-K1",
        }
        self.transactions["3476682"] = {
            "TransactionID": "3476682",
            "TransactionAmt": 482.12,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t6_base,
            "card_id": "C07297-K1",
            "customer_id": "C07297",
        }
        self.card_histories["C07297-K1"] = [
            self.transactions["3476675"],
            self.transactions["3476678"],
            self.transactions["3476680"],
            self.transactions["3476682"],
        ]
        self.shared_entities["3476682"] = {
            "connected_cards": ["C04812-K1"],
            "device_profiles": [dev6],
        }
        self.related_cases[dev6] = [
            {
                "case_id": "CC-0419",
                "outcome": "confirmed_fraud",
                "pattern": "card_testing",
            }
        ]

        # =========================================================================
        # HHG-007: Legitimate Travel (Customer C09933, Card C09933-K2, Txn 3514948)
        # =========================================================================
        t7_base = datetime(2016, 12, 5, 3, 46, 14)
        self.transactions["3514948"] = {
            "TransactionID": "3514948",
            "TransactionAmt": 111.92,
            "ProductCD": "W",
            "channel": "in_person",
            "addr1": "264.0",
            "ts": t7_base,
            "risk_score": 0.87,
            "card_id": "C09933-K2",
            "customer_id": "C09933",
        }
        self.card_histories["C09933-K2"] = [
            {
                "TransactionID": "3513010",
                "TransactionAmt": 45.00,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "264.0",
                "ts": t7_base - timedelta(days=2),
            },
            {
                "TransactionID": "3514022",
                "TransactionAmt": 88.50,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "264.0",
                "ts": t7_base - timedelta(days=1),
            },
            self.transactions["3514948"],
        ]
        self.shared_entities["3514948"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-008: Fraud Account Takeover (Customer C13171, Card C13171-K2, Txn 3558054)
        # Pattern: account_takeover
        # =========================================================================
        t8_base = datetime(2016, 12, 20, 3, 8, 56)
        dev8 = "Windows 7 | Firefox 50.0 | Proxy: Anonymous"
        self.transactions["3558050"] = {
            "TransactionID": "3558050",
            "TransactionAmt": 650.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t8_base - timedelta(hours=5),
            "card_id": "C13171-K2",
        }
        self.transactions["3558054"] = {
            "TransactionID": "3558054",
            "TransactionAmt": 55.68,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t8_base,
            "card_id": "C13171-K2",
            "customer_id": "C13171",
        }
        self.card_histories["C13171-K2"] = [
            {
                "TransactionID": "3550100",
                "TransactionAmt": 22.00,
                "ProductCD": "W",
                "channel": "in_person",
                "ts": t8_base - timedelta(hours=10),
            },
            self.transactions["3558050"],
            self.transactions["3558054"],
        ]
        self.shared_entities["3558054"] = {
            "connected_cards": ["C13171-K1"],
            "device_profiles": [dev8],
        }

        # =========================================================================
        # HHG-009: Legitimate commute/rideshare (Customer C08299, Card C08299-K1, Txn 3581141)
        # =========================================================================
        t9_base = datetime(2016, 12, 28, 17, 10, 53)
        self.transactions["3581141"] = {
            "TransactionID": "3581141",
            "TransactionAmt": 30.02,
            "ProductCD": "R",
            "channel": "online",
            "ts": t9_base,
            "card_id": "C08299-K1",
            "customer_id": "C08299",
        }
        self.card_histories["C08299-K1"] = [
            {
                "TransactionID": "3570010",
                "TransactionAmt": 28.50,
                "ProductCD": "R",
                "channel": "online",
                "ts": t9_base - timedelta(days=7),
            },
            self.transactions["3581141"],
        ]
        self.shared_entities["3581141"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-010: Fraud (Customer C10434, Card C10434-K1, Txn 3506725)
        # Pattern: card_not_present_new_device, exposure > $2,500
        # =========================================================================
        t10_base = datetime(2016, 12, 2, 18, 18, 27)
        dev10 = "Linux x86_64 | Chrome 53.0 | 1920x1080 | Proxy: Hidden"
        self.transactions["3506720"] = {
            "TransactionID": "3506720",
            "TransactionAmt": 1200.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t10_base - timedelta(hours=4),
            "card_id": "C10434-K1",
        }
        self.transactions["3506722"] = {
            "TransactionID": "3506722",
            "TransactionAmt": 1050.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t10_base - timedelta(hours=2),
            "card_id": "C10434-K1",
        }
        self.transactions["3506725"] = {
            "TransactionID": "3506725",
            "TransactionAmt": 1000.03,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t10_base,
            "risk_score": 0.90,
            "card_id": "C10434-K1",
            "customer_id": "C10434",
        }
        self.card_histories["C10434-K1"] = [
            self.transactions["3506720"],
            self.transactions["3506722"],
            self.transactions["3506725"],
        ]
        self.shared_entities["3506725"] = {
            "connected_cards": [],
            "device_profiles": [dev10],
        }

        # =========================================================================
        # HHG-011: Legitimate annual software renewal (Customer C11923, Card C11923-K2, Txn 3583368)
        # =========================================================================
        t11_base = datetime(2016, 12, 29, 6, 27, 44)
        self.transactions["3583368"] = {
            "TransactionID": "3583368",
            "TransactionAmt": 131.30,
            "ProductCD": "R",
            "channel": "online",
            "ts": t11_base,
            "card_id": "C11923-K2",
            "customer_id": "C11923",
        }
        self.card_histories["C11923-K2"] = [
            {
                "TransactionID": "3501001",
                "TransactionAmt": 45.00,
                "ProductCD": "W",
                "channel": "in_person",
                "ts": t11_base - timedelta(days=10),
            },
            self.transactions["3583368"],
        ]
        self.shared_entities["3583368"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-012: Fraud Out of Region Clone (Customer C05876, Card C05876-K2, Txn 3553342)
        # Pattern: out_of_region_use
        # =========================================================================
        t12_base = datetime(2016, 12, 18, 5, 0, 31)
        self.transactions["3553330"] = {
            "TransactionID": "3553330",
            "TransactionAmt": 15.00,
            "ProductCD": "W",
            "channel": "in_person",
            "addr1": "299.0",
            "ts": t12_base - timedelta(minutes=20),
            "card_id": "C05876-K2",
        }
        self.transactions["3553342"] = {
            "TransactionID": "3553342",
            "TransactionAmt": 30.91,
            "ProductCD": "W",
            "channel": "in_person",
            "addr1": "494.0",
            "ts": t12_base,
            "risk_score": 0.55,
            "card_id": "C05876-K2",
            "customer_id": "C05876",
        }
        self.card_histories["C05876-K2"] = [
            self.transactions["3553330"],
            self.transactions["3553342"],
        ]
        self.shared_entities["3553342"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-013: Legitimate (Customer C07671, Card C07671-K2, Txn 3526826)
        # =========================================================================
        t13_base = datetime(2016, 12, 9, 5, 39, 29)
        self.transactions["3526826"] = {
            "TransactionID": "3526826",
            "TransactionAmt": 35.66,
            "ProductCD": "R",
            "channel": "online",
            "id_15": "Found",
            "ts": t13_base,
            "risk_score": 0.76,
            "card_id": "C07671-K2",
            "customer_id": "C07671",
        }
        self.card_histories["C07671-K2"] = [
            {
                "TransactionID": "3511100",
                "TransactionAmt": 38.00,
                "ProductCD": "R",
                "channel": "online",
                "ts": t13_base - timedelta(days=4),
            },
            self.transactions["3526826"],
        ]
        self.shared_entities["3526826"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-014: Fraud Multi-card Device Ring (Customer C13487, Card C13487-K1, Txn 3478561)
        # Pattern: card_not_present_new_device, shared origin R6
        # =========================================================================
        t14_base = datetime(2016, 11, 22, 20, 11, 0)
        dev14 = "SAMSUNG SM-G935F | Android 7.0 | Samsung Browser | 2560x1440"
        self.transactions["3478550"] = {
            "TransactionID": "3478550",
            "TransactionAmt": 850.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t14_base - timedelta(hours=3),
            "card_id": "C13487-K1",
        }
        self.transactions["3478561"] = {
            "TransactionID": "3478561",
            "TransactionAmt": 620.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t14_base,
            "card_id": "C13487-K1",
            "customer_id": "C13487",
        }
        self.card_histories["C13487-K1"] = [
            self.transactions["3478550"],
            self.transactions["3478561"],
        ]
        self.shared_entities["3478561"] = {
            "connected_cards": ["C04812-K1", "C07297-K1", "C09214-K2"],
            "device_profiles": [dev14],
        }
        self.related_cases[dev14] = [
            {
                "case_id": "CC-0419",
                "outcome": "confirmed_fraud",
                "pattern": "card_testing",
            },
            {
                "case_id": "CC-2671",
                "outcome": "confirmed_fraud",
                "pattern": "card_not_present_new_device",
            },
        ]

        # =========================================================================
        # HHG-015: Legitimate Electronics (Customer C03042, Card C03042-K1, Txn 3464869)
        # =========================================================================
        t15_base = datetime(2016, 11, 17, 19, 3, 36)
        self.transactions["3464869"] = {
            "TransactionID": "3464869",
            "TransactionAmt": 599.94,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "Found",
            "ts": t15_base,
            "risk_score": 0.77,
            "card_id": "C03042-K1",
            "customer_id": "C03042",
        }
        self.card_histories["C03042-K1"] = [
            {
                "TransactionID": "3411002",
                "TransactionAmt": 520.00,
                "ProductCD": "C",
                "channel": "online",
                "ts": t15_base - timedelta(days=25),
            },
            self.transactions["3464869"],
        ]
        self.shared_entities["3464869"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-016: Fraud (Customer C09988, Card C09988-K1, Txn 3534820)
        # Pattern: card_testing
        # =========================================================================
        t16_base = datetime(2016, 12, 12, 1, 39, 8)
        self.transactions["3534810"] = {
            "TransactionID": "3534810",
            "TransactionAmt": 0.99,
            "channel": "online",
            "ts": t16_base - timedelta(minutes=45),
            "card_id": "C09988-K1",
        }
        self.transactions["3534812"] = {
            "TransactionID": "3534812",
            "TransactionAmt": 1.50,
            "channel": "online",
            "ts": t16_base - timedelta(minutes=30),
            "card_id": "C09988-K1",
        }
        self.transactions["3534815"] = {
            "TransactionID": "3534815",
            "TransactionAmt": 2.00,
            "channel": "online",
            "ts": t16_base - timedelta(minutes=15),
            "card_id": "C09988-K1",
        }
        self.transactions["3534820"] = {
            "TransactionID": "3534820",
            "TransactionAmt": 59.67,
            "ProductCD": "C",
            "channel": "online",
            "ts": t16_base,
            "card_id": "C09988-K1",
            "customer_id": "C09988",
        }
        self.card_histories["C09988-K1"] = [
            self.transactions["3534810"],
            self.transactions["3534812"],
            self.transactions["3534815"],
            self.transactions["3534820"],
        ]
        self.shared_entities["3534820"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-017: Fraud (Customer C04570, Card C04570-K1, Txn 3450629)
        # Pattern: card_not_present_new_device, shared device
        # =========================================================================
        t17_base = datetime(2016, 11, 12, 0, 46, 24)
        dev17 = "SAMSUNG SM-G892A Build/NRD90M | Android 7.0 | samsung browser 6.2 | 2220x1080"
        self.transactions["3450625"] = {
            "TransactionID": "3450625",
            "TransactionAmt": 550.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t17_base - timedelta(hours=4),
            "card_id": "C04570-K1",
        }
        self.transactions["3450628"] = {
            "TransactionID": "3450628",
            "TransactionAmt": 450.00,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t17_base - timedelta(hours=2),
            "card_id": "C04570-K1",
        }
        self.transactions["3450629"] = {
            "TransactionID": "3450629",
            "TransactionAmt": 100.09,
            "ProductCD": "C",
            "channel": "online",
            "id_15": "New",
            "ts": t17_base,
            "risk_score": 0.57,
            "card_id": "C04570-K1",
            "customer_id": "C04570",
        }
        self.card_histories["C04570-K1"] = [
            self.transactions["3450625"],
            self.transactions["3450628"],
            self.transactions["3450629"],
        ]
        self.shared_entities["3450629"] = {
            "connected_cards": ["C00877-K1"],
            "device_profiles": [dev17],
        }
        self.related_cases[dev17] = [
            {
                "case_id": "CC-0141",
                "outcome": "confirmed_fraud",
                "pattern": "card_not_present_new_device",
            }
        ]

        # =========================================================================
        # HHG-018: Legitimate Supermarket (Customer C02354, Card C02354-K2, Txn 3491361)
        # =========================================================================
        t18_base = datetime(2016, 11, 27, 14, 41, 26)
        self.transactions["3491361"] = {
            "TransactionID": "3491361",
            "TransactionAmt": 39.08,
            "ProductCD": "W",
            "channel": "in_person",
            "addr1": "315.0",
            "ts": t18_base,
            "card_id": "C02354-K2",
            "customer_id": "C02354",
        }
        self.card_histories["C02354-K2"] = [
            {
                "TransactionID": "3481001",
                "TransactionAmt": 42.15,
                "ProductCD": "W",
                "channel": "in_person",
                "addr1": "315.0",
                "ts": t18_base - timedelta(days=4),
            },
            self.transactions["3491361"],
        ]
        self.shared_entities["3491361"] = {"connected_cards": [], "device_profiles": []}

        # =========================================================================
        # HHG-019: Undocumented Coordinated Abuse (Customer C07987, Card C07987-K2, Txn 3503878)
        # Pattern: undocumented, R9
        # =========================================================================
        t19_base = datetime(2016, 12, 1, 22, 28, 53)
        dev19 = "Mac OS X | Chrome 54.0 | 2560x1600 | Proxy: Anonymous"
        self.transactions["3503870"] = {
            "TransactionID": "3503870",
            "TransactionAmt": 900.00,
            "ProductCD": "S",
            "channel": "online",
            "id_15": "New",
            "ts": t19_base - timedelta(hours=6),
            "card_id": "C07987-K2",
        }
        self.transactions["3503875"] = {
            "TransactionID": "3503875",
            "TransactionAmt": 900.00,
            "ProductCD": "S",
            "channel": "online",
            "id_15": "New",
            "ts": t19_base - timedelta(hours=3),
            "card_id": "C07987-K2",
        }
        self.transactions["3503878"] = {
            "TransactionID": "3503878",
            "TransactionAmt": 99.92,
            "ProductCD": "S",
            "channel": "online",
            "id_15": "New",
            "ts": t19_base,
            "risk_score": 0.90,
            "card_id": "C07987-K2",
            "customer_id": "C07987",
        }
        self.card_histories["C07987-K2"] = [
            self.transactions["3503870"],
            self.transactions["3503875"],
            self.transactions["3503878"],
        ]
        self.shared_entities["3503878"] = {
            "connected_cards": ["C04910-K1", "C06621-K3"],
            "device_profiles": [dev19],
        }

        # =========================================================================
        # HHG-020: Legitimate (Customer C12265, Card C12265-K2, Txn 3509359)
        # =========================================================================
        t20_base = datetime(2016, 12, 3, 12, 4, 26)
        self.transactions["3509359"] = {
            "TransactionID": "3509359",
            "TransactionAmt": 125.08,
            "ProductCD": "W",
            "channel": "online",
            "id_15": "Found",
            "ts": t20_base,
            "risk_score": 0.52,
            "card_id": "C12265-K2",
            "customer_id": "C12265",
        }
        self.card_histories["C12265-K2"] = [
            {
                "TransactionID": "3499000",
                "TransactionAmt": 110.00,
                "ProductCD": "W",
                "channel": "online",
                "ts": t20_base - timedelta(days=6),
            },
            self.transactions["3509359"],
        ]
        self.shared_entities["3509359"] = {"connected_cards": [], "device_profiles": []}
