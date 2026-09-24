from typing import Any, Dict, List

from backend.services.graph_models import GraphEdge, GraphNode, GraphResponse


class CaseGraphService:
    """
    Builds a graph representation for an investigation case.

    This currently uses the development in-memory graph client.
    The service can later be connected to the real TigerGraph client
    without changing the frontend graph contract.
    """

    def __init__(self, graph_client: Any) -> None:
        self.graph = graph_client

    def build_case_graph(
        self,
        case_id: str,
        customer_id: str,
        card_id: str,
        transaction_id: str,
    ) -> GraphResponse:
        transaction = self.graph.get_transaction(transaction_id)

        if not transaction:
            raise ValueError(
                f"Transaction '{transaction_id}' was not found by the graph client."
            )

        shared_entities: Dict[str, List[str]] = (
            self.graph.get_shared_entities(transaction_id) or {}
        )

        connected_cards = [
            str(value)
            for value in shared_entities.get("connected_cards", [])
            if value is not None
        ]

        device_profiles = [
            str(value)
            for value in shared_entities.get("device_profiles", [])
            if value is not None
        ]

        related_cases = (
            self.graph.get_related_cases(device_profiles) or []
        )

        nodes: List[GraphNode] = [
            GraphNode(
                id=case_id,
                label=case_id,
                type="case",
                metadata={"role": "investigation_case"},
            ),
            GraphNode(
                id=customer_id,
                label=customer_id,
                type="customer",
                metadata={"role": "customer"},
            ),
            GraphNode(
                id=card_id,
                label=card_id,
                type="card",
                metadata={"role": "primary_card"},
            ),
            GraphNode(
                id=transaction_id,
                label=transaction_id,
                type="transaction",
                metadata={
                    "role": "flagged_transaction",
                    "amount": str(transaction.get("amount", "")),
                    "channel": str(transaction.get("channel", "")),
                    "region": str(transaction.get("region", "")),
                },
            ),
        ]

        edges: List[GraphEdge] = [
            GraphEdge(
                source=case_id,
                target=transaction_id,
                relationship="INVESTIGATES",
            ),
            GraphEdge(
                source=customer_id,
                target=card_id,
                relationship="OWNS",
            ),
            GraphEdge(
                source=card_id,
                target=transaction_id,
                relationship="USED_FOR",
            ),
        ]

        for device_id in device_profiles:
            nodes.append(
                GraphNode(
                    id=device_id,
                    label=device_id,
                    type="device",
                    metadata={"role": "device_profile"},
                )
            )

            edges.append(
                GraphEdge(
                    source=transaction_id,
                    target=device_id,
                    relationship="USES",
                )
            )

        for connected_card_id in connected_cards:
            if connected_card_id == card_id:
                continue

            nodes.append(
                GraphNode(
                    id=connected_card_id,
                    label=connected_card_id,
                    type="card",
                    metadata={"role": "connected_card"},
                )
            )

            edges.append(
                GraphEdge(
                    source=transaction_id,
                    target=connected_card_id,
                    relationship="SHARED_WITH",
                )
            )

        for related_case in related_cases:
            related_case_id = str(
                related_case.get("case_id")
                or related_case.get("CaseID")
                or related_case.get("id")
                or ""
            )

            if not related_case_id:
                continue

            nodes.append(
                GraphNode(
                    id=related_case_id,
                    label=related_case_id,
                    type="case",
                    metadata={"role": "related_case"},
                )
            )

            for device_id in device_profiles:
                edges.append(
                    GraphEdge(
                        source=device_id,
                        target=related_case_id,
                        relationship="LINKED_TO",
                    )
                )

        return GraphResponse(
            case_id=case_id,
            nodes=self._deduplicate_nodes(nodes),
            edges=self._deduplicate_edges(edges),
        )

    @staticmethod
    def _deduplicate_nodes(
        nodes: List[GraphNode],
    ) -> List[GraphNode]:
        unique: Dict[str, GraphNode] = {}

        for node in nodes:
            unique[node.id] = node

        return list(unique.values())

    @staticmethod
    def _deduplicate_edges(
        edges: List[GraphEdge],
    ) -> List[GraphEdge]:
        unique: Dict[tuple[str, str, str], GraphEdge] = {}

        for edge in edges:
            key = (
                edge.source,
                edge.target,
                edge.relationship,
            )
            unique[key] = edge

        return list(unique.values())
