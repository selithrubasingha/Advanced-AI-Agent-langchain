from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import json
import textwrap

from models import State, FinalSynthesis, Analysis
from web_actions import (serp_search, youtube_search_api)
from prompts import (
    get_google_analysis_messages,
    get_youtube_analysis_messages,
    get_synthesis_messages

)

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


def google_search(state: State):
    user_question = state.get("user_question")

    google_results = serp_search(user_question)

    google_results_str = json.dumps(google_results, indent=2)  # Convert to string
    return {"google_results": google_results_str}


def youtube_search(state: State):
    user_question = state.get("user_question")

    youtube_results = youtube_search_api(user_question)
    youtube_results_str = json.dumps(youtube_results, indent=2)  # Convert to string
    return {"youtube_results": youtube_results_str}


def analyze_google_results(state: State):
    user_question = state.get("user_question", "")
    google_results = state.get("google_results", "")

    messages = get_google_analysis_messages(user_question, google_results)
    structured_llm = llm.with_structured_output(Analysis)
    reply = structured_llm.invoke(messages)

    return {"google_analysis": reply}


def analyze_youtube_results(state: State):
    user_question = state.get("user_question", "")
    youtube_results = state.get("youtube_results", "")

    messages = get_youtube_analysis_messages(user_question, youtube_results)
    structured_llm = llm.with_structured_output(Analysis)
    reply = structured_llm.invoke(messages)

    return {"youtube_analysis": reply}

def format_final_answer(synthesis: FinalSynthesis, query: str) -> str:
    """Helper function to format the FinalSynthesis object into a clean string."""

    output = textwrap.dedent(f"""
    Here are the top 6 courses I found for your query: "{query}"

    I have selected the 3 best from Google and 3 from YouTube and ranked them based on relevance, topics covered, and clarity.
    """)

    output += "\n" + "=" * 30 + "\n\n"

    if not synthesis.ranked_courses:
        return "Sorry, I was unable to find any courses matching your query."

    # Sort courses by rank
    ranked_list = sorted(synthesis.ranked_courses, key=lambda c: c.rank)

    for course in ranked_list:
        output += f"### 🥇 Rank {course.rank}: {course.course_name} ({course.website_name})\n"
        output += f"**Time:** {course.course_time or 'Not specified'}\n"

        cost = "Not specified"
        if course.free_course is True:
            cost = "Free"
        elif course.free_course is False:
            cost = "Paid"
        output += f"**Cost:** {cost}\n"

        output += f"**Description:** {course.description}\n"
        output += f"**Topics:** {', '.join(course.course_topics)}\n"
        output += f"**Justification:** {course.justification}\n\n"

    return output



def synthesize_analyses(state: State):
    pass
    #get the question as well as the all the seperate answers
    user_question = state.get("user_question", "")
    google_analysis = state.get("google_analysis")
    youtube_analysis = state.get("youtube_analysis")

    # Add a check for safety
    if not google_analysis or not youtube_analysis:
        error_msg = "Sorry, one of the analysis steps failed. I cannot provide a final answer."
        return {"final_answer": error_msg, "messages": [{"role": "assistant", "content": error_msg}]}
    # --- END FIX 1 ---

    #combine those answers into one
    messages = get_synthesis_messages(
        user_question, google_analysis, youtube_analysis
    )

    #invoke it for the last time bro
    structured_llm = llm.with_structured_output(FinalSynthesis)
    reply = structured_llm.invoke(messages)
    #fill the content of invoke as the final answer
    final_answer = reply
    final_answer_str = format_final_answer(final_answer,user_question)

    return {"final_answer": final_answer_str, "messages": [{"role": "assistant", "content": final_answer_str}]}



graph = StateGraph(State)

graph.add_node("google_search", google_search)
graph.add_node("youtube_search", youtube_search)
graph.add_node("analyze_google_results", analyze_google_results)
graph.add_node("analyze_youtube_results", analyze_youtube_results)
graph.add_node("synthesize_analyses", synthesize_analyses)

# connect nodes linearly and compile
graph.add_edge(START, "google_search")
graph.add_edge("google_search", "youtube_search")
graph.add_edge("youtube_search", "analyze_google_results")
graph.add_edge("analyze_google_results", "analyze_youtube_results")
graph.add_edge("analyze_youtube_results", "synthesize_analyses")
graph.add_edge("synthesize_analyses", END)

app = graph.compile()

def run_chatbot():
    print("Multi-Source Research Agent")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("Ask me anything: ")
        if user_input.lower() == "exit":
            print("Bye")
            break

        state = {
            "messages": [{"role": "user", "content": user_input}],
            "user_question": user_input,
            "google_results": None,
            "youtube_results": None,
            "google_analysis": None,
            "youtube_analysis": None,
            "final_answer": None,
        }

        print("\nStarting parallel research process...")
        print("Launching Google and YouTube searches...\n")
        final_state = app.invoke(state)

        if final_state.get("final_answer"):
            print(f"\nFinal Answer:\n{final_state.get('final_answer')}\n")

        print("-" * 80)

if __name__ == "__main__":
    run_chatbot()