from dotenv import load_dotenv
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from models import State , OutputStructure

llm= ChatOpenAI(model="gpt-4o-mini")

def google_search(state: State):
    pass

def youtube_search(state:State):
    pass

def analyze_google_results(state:State):
    pass

def analyze_youtube_results(state:State):
    pass


def synthesize_analyses(state:State):
    pass

graph = StateGraph(State)

graph.add_node("google_search",google_search)
graph.add_node("youtube_search",youtube_search)
graph.add_node("analyze_google_results",analyze_google_results)
graph.add_node("analyze_youtube_results",analyze_youtube_results)
graph.add_node("synthesize_analyses", synthesize_analyses)

# connect nodes linearly and compile
graph.add_edge(START, "google_search")
graph.add_edge("google_search", "youtube_search")
graph.add_edge("youtube_search", "analyze_google_results")
graph.add_edge("analyze_google_results", "analyze_youtube_results")
graph.add_edge("analyze_youtube_results", "synthesize_analyses")
graph.add_edge("synthesize_analyses", END)

graph.compile()

