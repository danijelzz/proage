from typing import List
from langchain_core.tools import tool

@tool
def check_medication_conflicts(medications: List[str]) -> str:
    """
    Provjerava bazu podataka za potencijalne opasne interakcije i konflikte
    između navedenih lijekova. Vraća tekstualno izvješće o konfliktima.
    """

    medication_set = {m.lower() for m in medications}

    warnings = []

    dangerous_pairs = [
        (
            {"andol", "brufen"},
            "Andol + Brufen mogu povećati rizik od želučanog krvarenja."
        ),
        (
            {"aspirin", "ibuprofen"},
            "Aspirin + Ibuprofen mogu povećati rizik od krvarenja."
        ),
        (
            {"normabel", "xanax"},
            "Normabel + Xanax mogu izazvati pretjeranu sedaciju i omamljenost."
        ),
        (
            {"warfarin", "andol"},
            "Warfarin + Andol značajno povećavaju rizik od krvarenja."
        ),
    ]

    for pair, message in dangerous_pairs:
        if pair.issubset(medication_set):
            warnings.append(message)

    if not warnings:
        return "Nisu pronađene poznate ozbiljne interakcije među navedenim lijekovima."

    return "\n".join(warnings)