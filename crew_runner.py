import os
import asyncio

from crewai import Agent, Task, Crew
from crewai.tools import tool

# MCP client (python-sdk)
from mcp.client.stdio import stdio_client
from mcp import ClientSession

MCP_CMD = ["python", "mcp_server.py"]

async def mcp_call(tool_name: str, arguments: dict):
    async with stdio_client(MCP_CMD) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            # result.content is structured; simplest is return as text/dict-ish
            return result.content

@tool("Get provider slots")
def get_slots_tool(provider_id: str, day: str):
    """Get available slots for a provider_id on day (YYYY-MM-DD)."""
    return asyncio.run(mcp_call("get_slots", {"provider_id": provider_id, "day": day}))

@tool("Book appointment slot")
def book_slot_tool(provider_id: str, patient_id: str, start_at: str, end_at: str):
    """Book a slot for patient. start_at/end_at: YYYY-MM-DD HH:MM"""
    return asyncio.run(mcp_call("book_slot", {
        "provider_id": provider_id,
        "patient_id": patient_id,
        "start_at": start_at,
        "end_at": end_at
    }))

@tool("Get patient record")
def get_patient_tool(patient_id: str):
    """Fetch patient record."""
    return asyncio.run(mcp_call("get_patient", {"patient_id": patient_id}))

def main():
    scheduler_agent = Agent(
        role="Clinic Scheduling Assistant",
        goal="Help patients find slots and book appointments safely.",
        backstory="You assist patients by calling tools to check provider availability and book appointments.",
        tools=[get_slots_tool, book_slot_tool, get_patient_tool],
        verbose=True,
        allow_delegation=False
    )

    task = Task(
        description=(
            "User asked: {user_question}\n"
            "If booking is requested, confirm the details in your response before booking."
        ),
        expected_output="A helpful response. If booking, include confirmation of slot time and provider.",
        agent=scheduler_agent
    )

    crew = Crew(agents=[scheduler_agent], tasks=[task], verbose=True)
    user_question = input("Ask: ")
    result = crew.kickoff(inputs={"user_question": user_question})
    print("\n---\n", result)

if __name__ == "__main__":
    main()
