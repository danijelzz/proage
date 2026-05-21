import re

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

from state import HealthState
from prompts import (
    DIAGNOSTIC_PROMPT,
    MEDICATION_PROMPT,
    SUMMARY_PROMPT,
)

from tools import check_medication_conflicts

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5",
    temperature=0,
    api_key=os.environ.get("OPENAI_API_KEY")
)


tools = [check_medication_conflicts]
llm_with_tools = llm.bind_tools(tools)

def extract_section(text: str, section_name: str):
    pattern = rf"{section_name}:(.*?)(\n[A-ZČĆŽŠĐ]+:|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    
    if not match:
        return []
    
    content = match.group(1).strip()
    lines = [
        line.replace("-", "").strip()
        for line in content.split("\n")
        for line in content.split("\n")
        if line.strip()
    ]
    return lines


# =========================
# AGENT 1: DIAGNOSTIC AGENT
# =========================

def diagnostic_agent(state: HealthState):
    prompt = f"""
{DIAGNOSTIC_PROMPT}

KORISNIČKI UNOS:
{state["user_input"]}
"""
    response = llm.invoke(prompt)
    text = response.content

    diagnoses = extract_section(text, "DIJAGNOZE")
    medications = extract_section(text, "LIJEKOVI")

    return {
        "diagnoses": diagnoses,
        "medications": medications,
        "diagnostic_report": text,
        "messages": [HumanMessage(content=f"Lijekovi za analizu: {', '.join(medications)}")]
    }


# =========================
# AGENT 2: MEDICATION AGENT
# =========================

def medication_agent(state: HealthState):
    messages = state["messages"]
    
    if not any(isinstance(m, SystemMessage) for m in messages):
        system_prompt = SystemMessage(content=MEDICATION_PROMPT)
        messages = [system_prompt] + messages

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "medication_report": response.content if not response.tool_calls else ""
    }


# =========================
# AGENT 3: SUMMARY AGENT
# =========================

def summary_agent(state: HealthState):
    prompt = SUMMARY_PROMPT.format(
        diagnostic_report=state["diagnostic_report"],
        medication_report=state["medication_report"]
    )

    response = llm.invoke(prompt)

    return {
        "final_summary": response.content
    }


# =========================
# GRAPH CONFIGURATION
# =========================

builder = StateGraph(HealthState)

builder.add_node("diagnostic_agent", diagnostic_agent)
builder.add_node("medication_agent", medication_agent)
builder.add_node("summary_agent", summary_agent)

builder.add_node("tools", ToolNode(tools))

builder.set_entry_point("diagnostic_agent")

builder.add_edge("diagnostic_agent", "medication_agent")

builder.add_conditional_edges(
    "medication_agent",
    tools_condition, # Provjerava sadrži li zadnja poruka zahtjev za alatom
    {
        "tools": "tools",       # Ako sadrži -> idi na čvor "tools"
        END: "summary_agent"    # Ako NE sadrži -> završi i idi na summary_agent
    }
)

builder.add_edge("tools", "medication_agent")

builder.add_edge("summary_agent", END)

graph = builder.compile()