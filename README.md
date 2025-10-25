# Course Finder Agent

## The Problem: LLM Hallucinations

Generative AI models, while powerful, sometimes "hallucinate" – providing inaccurate information or links to resources (like online courses or YouTube videos) that don't actually exist. This can be frustrating when trying to find reliable learning materials.

---

## The Solution: Real-Time Search and Synthesis

This project tackles the hallucination problem by building a **LangGraph agent** that finds and ranks online learning resources based on real-time data. Instead of relying solely on the LLM's internal knowledge, it actively searches the web and YouTube for relevant courses.

---
## Things I learned...

I wanted to make this project to improve my ability to build an advanced AI agent , This project gave me a better understanding of how to use langchain.
I also learned using API services from third party providers . structuring a project with organized .py files and also improved cli commands relating to git
___

## How it Works

The agent follows these steps when you provide a course topic (e.g., "javascript course"):

1.  **Query Input:** Takes your desired course topic as input.
2.  **Multi-Source Search:**
    * Uses the **Bright Data SERP API** to perform a Google Search for relevant courses.
    * Uses the **Bright Data YouTube Scraper** (simulated or real, via `Youtube_api`) to find relevant YouTube video courses/tutorials.
3.  **Data Extraction & Analysis:**
    * Employs a Large Language Model (LLM, specifically `gpt-4o-mini` via LangChain) with structured output capabilities (`with_structured_output`).
    * Parses the Google search results and YouTube video data (including titles, descriptions, transcripts) to extract key details (course name, platform, topics, duration, cost) using predefined Pydantic models (`OutputStructure`, `Analysis`).
4.  **Synthesis & Ranking:**
    * A final LLM step analyzes the extracted course lists from both Google and YouTube.
    * It selects the **top 3 courses from each source**.
    * It ranks these 6 courses based on relevance, content quality, and clarity, providing a justification for each rank.
5.  **Formatted Output:** Presents the final ranked list in a clean, readable format using a Pydantic model (`FinalSynthesis`, `RankedCourse`).

---

## Key Features

* **LangGraph Orchestration:** Uses LangGraph to define and run the multi-step agent workflow.
* **Real-Time Data:** Leverages Bright Data APIs for up-to-date search and video information, minimizing hallucinations.
* **Structured Output:** Utilizes Pydantic models and LangChain's `with_structured_output` to ensure reliable data extraction from the LLM.
* **Multi-Source Synthesis:** Combines and ranks results from both Google web search and YouTube for a comprehensive overview.
* **Clear Ranking & Justification:** Provides a ranked list with explanations for why each course was chosen.

---

## Technology Stack

* **Programming Language:** Python
* **Orchestration:** LangGraph
* **LLM Interaction:** LangChain, `langchain-openai` (using `gpt-4o-mini`)
* **Data Modeling:** Pydantic
* **Web Search:** Bright Data SERP API (via `web_actions.py`)
* **YouTube Scraping:** Bright Data Scraper API (via `web_actions.py`)
* **Environment Management:** `python-dotenv`

---

## Setup and Running

* ** You can clone this git repo but you should also add an .env file and include an OPENAI_API_KEY and a BRIGHTDATA_API_KEY from the relavent websites

