from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages


class HealthState(TypedDict):
    user_input: str

    diagnoses: List[str]
    medications: List[str]

    diagnostic_report: str
    medication_report: str

    final_summary: str

    messages: Annotated[list, add_messages]