import asyncio
import os
import random
import string

from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.core.agent import AgentStream
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone
import streamlit as st
import candidates_list

load_dotenv()


# TOOLS list
# TOOLS list
def open_application_from_desktop(app_name: str):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut = os.path.join(desktop, f"{app_name}.lnk")
    os.startfile(shortcut)


open_app_tool = FunctionTool.from_defaults(
    fn=open_application_from_desktop,
    name="open_application",
    description="Open a desktop application shortcut by providing its name.",
)


def generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(random.choice(chars) for _ in range(length))


password_tool = FunctionTool.from_defaults(
    fn=generate_password,
    name="generate_password",
    description="Generate a random password with a specified length.",
)


def get_fun_fact(topic: str) -> str:
    facts = {
        "moon": "The Moon is drifting away from Earth at about 3.8 cm per year.",
        "python": "Python was named after Monty Python, not the snake.",
        "coffee": "Coffee beans are actually seeds inside red or purple fruits called coffee cherries.",
    }

    return facts.get(topic.lower(), f"No fun fact available for {topic}.")


fun_fact_tool = FunctionTool.from_defaults(
    fn=get_fun_fact,
    name="general_knowledge",
    description="Provide a fun fact about a given topic.",
)


def inquire_information(query_prompt: str):
    # INQUIRES DATA FROM PINECONE DB
    pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    pinecone_index = pinecone.Index("llamaindex-document-helper")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    query_engine = index.as_query_engine()

    return query_engine.query(query_prompt)


inquire_candidate_info = FunctionTool.from_defaults(
    fn=inquire_information,
    name="inquire_candidate_info",
    description="Search and retrieve candidate information from the Pinecone vector index. Use this tool when the user asks about a candidate's profile, skills, or background and other info about candidates ",
)
# TOOLS list
# TOOLS list


# Agent initialization
# Agent initialization
llm = OpenAI(model="gpt-4o-mini", temperature=0.3)

agent = ReActAgent(
    tools=[open_app_tool, password_tool, fun_fact_tool, inquire_candidate_info], llm=llm
)

ctx = Context(agent)


async def run_agent(user_prompt: str):
    handler = agent.run(user_prompt, ctx=ctx)
    collected = ""
    async for ev in handler.stream_events():
        if isinstance(ev, AgentStream):
            collected += ev.delta
    response = await handler
    return collected, response

st.set_page_config(page_title="Agent Chat", page_icon="🤖")
st.title("🤖 Chat with  ReAct Agent with toolkit")

st.sidebar.header("🛠 Agent Tools")
tools_info = [
    {
        "name": "Generate Password",
        "description": "Generate a random password with a specified length.",
    },
    {
        "name": "Fan fact about moon, coffe or python",
        "description": "Provide a fun fact about a given topic.",
    },
    {
        "name": "Inquire candidate info",
        "description": "Search and retrieve candidate information from the Pinecone vector index.",
    },
]
for tool in tools_info:
    st.sidebar.markdown(f"**{tool['name']}** — {tool['description']}")


candidates = candidates_list.CANDIDATES
for candidate in candidates:
    col1, col2, col3 = st.columns([2, 3, 2])
    col1.write(candidate["name"])
    col2.write(candidate["role"])
    if col3.button("Details", key=candidate["name"]):
        with st.expander(f"Info about {candidate['name']}", expanded=True):
            st.write(f"### {candidate['name']}")
            st.write(f"**Title:** {candidate['role']}")
            st.write(f"{candidate['info']}")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    streamed, final_response = loop.run_until_complete(run_agent(prompt))
    st.session_state["messages"].append(
        {"role": "assistant", "content": final_response}
    )
    with st.chat_message("assistant"):
        st.markdown(final_response)
