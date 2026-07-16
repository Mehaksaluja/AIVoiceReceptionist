from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from src.agent.prompts import build_system_prompt
from src.agent.tools import TOOLS
from src.config import settings
from src.models.booking import Session
from src.services.session_store import store

_agent = None


def _build_llm() -> ChatOpenAI:
    if not settings.has_openai:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to backend/.env before chatting with the agent."
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )


def create_agent_graph():
    return create_react_agent(
        model=_build_llm(),
        tools=TOOLS,
    )


def get_agent():
    global _agent
    if _agent is None:
        _agent = create_agent_graph()
    return _agent


def _history_to_messages(session: Session) -> list:
    messages: list = []
    for turn in session.history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


async def run_turn(session: Session, user_message: str) -> str:
    store.log(session.session_id, "user_message", user_message)

    system = build_system_prompt(
        patient_name=session.booking.name,
        patient_phone=session.booking.phone,
        appointment_reason=session.booking.reason,
        booking_id=session.booking.id,
        session_id=session.session_id,
    )

    prior = _history_to_messages(session)
    prior.append(HumanMessage(content=user_message))

    agent = get_agent()
    result = await agent.ainvoke(
        {
            "messages": [SystemMessage(content=system), *prior],
        }
    )

    messages = result.get("messages", [])
    reply = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content and not getattr(msg, "tool_calls", None):
            reply = msg.content if isinstance(msg.content, str) else str(msg.content)
            break

    if not reply:
        reply = "I'm sorry, I didn't catch that. Could you say that again?"

    session.history.append({"role": "user", "content": user_message})
    session.history.append({"role": "assistant", "content": reply})
    store.save(session)

    store.log(session.session_id, "agent_reply", reply)

    refreshed = store.get(session.session_id)
    if refreshed and refreshed.is_booked:
        store.log(session.session_id, "conversation_complete", "Booking flow finished")

    return reply


async def start_conversation(session: Session) -> str:
    opening = (
        f"Hello, please start the appointment conversation. "
        f"Greet {session.booking.name} and offer the first available slot using your tools."
    )
    return await run_turn(session, opening)
