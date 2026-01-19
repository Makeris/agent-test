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
    description="Query candidate information stored in Pinecone index.",
)
# TOOLS list
# TOOLS list



# Agent initialization
# Agent initialization
llm = OpenAI(model="gpt-4o-mini", temperature=0.3)

agent = ReActAgent(tools=[open_app_tool, password_tool, fun_fact_tool, inquire_candidate_info], llm=llm)

ctx = Context(agent)

async def main():
    user_prompt = "Do we have candidates? Open Discord on my desktop, then give me fact about coffe, and create password with 10 symbols"

    handler = agent.run(user_prompt, ctx=ctx)

    async for ev in handler.stream_events():
        if isinstance(ev, AgentStream):
            print(f"{ev.delta}", end="", flush=True)
    response = await handler
    print("\nFinal response:", response)


asyncio.run(main())
