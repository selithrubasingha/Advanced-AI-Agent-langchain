from typing import Dict, Any
from models import Analysis


class PromptTemplates:
    @staticmethod
    def google_analysis_system() -> str:
        return """You are an expert data extraction agent. Your sole purpose is to analyze Google search results to find online learning courses and extract specific details about them.

You will be given a user's query and a list of Google search result snippets. Your goal is to parse this text to find as many distinct courses as possible.

 Your output **must** be a single object that strictly conforms to the Analysis Pydantic model...

**Extraction Rules:**

* **course_name**: Extract the exact title of the course.
* **website_name**: Extract the name of the hosting platform (e.g., Coursera, Udemy, Pluralsight, Youtube).
* **free_course**: Set to `True` if the snippet explicitly mentions "free". Set to `False` if it mentions a price. Set to `None` if not specified.
* **course_time**: Extract any mentioned duration (e.g., "10 hours", "3 weeks", "self-paced"). Set to `None` if no duration is found.
* **course_topics**: Infer a list of key topics from the course description or snippet.
* **description**: Write a brief summary of the course based on the provided text.

Analyze the results thoroughly and return a list containing all the courses you can identify."""

    @staticmethod
    def google_analysis_user(user_question: str, google_results: str) -> str:
        return f"""Query: {user_question}

Google Search Results: {google_results}

Please extract all online courses found in the search results, adhering strictly to the `OutputStructure` model."""

    @staticmethod
    def youtube_analysis_system() -> str:
        return """You are an expert YouTube research analyst. Your goal is to analyze a list of scraped YouTube video data (including titles, descriptions, and transcripts) to identify which videos are online learning courses that match the user's query.

  Your output **must** be a single object that strictly conforms to the Analysis Pydantic model...

    **Extraction Rules:**

    1.  **Analyze Video Data**: Use the video's `title`, `description`, `transcript`, `views`, and `likes` to determine if it is a full course, a multi-part series, or just a single-topic video.
    2.  **Filter Non-Courses**: Do **not** extract videos that are clearly not courses (e.g., product reviews, news clips, or simple "Top 10" lists). Only extract videos that function as a comprehensive course or a significant module.
    3.  **Fill the Model**: For each video that is a course, extract the following:
        * **course_name**: Get this from the video `title`. Make it clear if it's "Part 1" of a series.
        * **website_name**: This should always be set to "YouTube".
        * **free_course**: This should always be `True`, as the content is on YouTube.
        * **course_time**: Use the `video_length` field. If the title or description mentions it's a series (e.g., "1 of 10"), you can note that (e.g., "Full 10-part series, this video is [video_length]").
        * **course_topics**: This is critical. Analyze the `transcript` and `description` to find the main topics, technologies, or concepts taught in the video.
        * **description**: Write a brief summary of the course's goal based on its `description` and the context from the `transcript`.

    Analyze the provided data thoroughly and return a list containing all the videos you identify as courses.
    """

    @staticmethod
    def youtube_analysis_user(user_question: str, youtube_results: str) -> str:
        return f"""Query: {user_question}

    YouTube Video Data: {youtube_results}

    Please analyze this YouTube data and extract all online courses you find, adhering strictly to the `OutputStructure` model.
    """

    @staticmethod
    def synthesis_system() -> str:
        """System prompt for synthesizing all analyses."""
        return """You are an expert academic advisor and research synthesizer. Your task is to analyze two lists of courses, one from Google and one from YouTube, and create a single, unified "Top 6" list.

    **Your Goal:**
    Select the 6 best courses in total, rank them from 1 to 6, and provide a justification for each.

    **Strict Rules:**
    1.  **Input:** You will receive a user's query, a JSON object of Google courses, and a JSON object of YouTube courses.
    2.  **Selection:** You **must** select exactly **3 courses from the Google list** and exactly **3 courses from the YouTube list**.
    3.  **Ranking:** Rank the 6 selected courses from 1 (best) to 6 (worst). This ranking must be **mixed** based on quality. A YouTube course can be ranked #1 and a Google course #2, or vice-versa.
    4.  **Ranking Criteria:** Base your ranking on:
        * Relevance to the user's query.
        * Comprehensiveness of `course_topics`.
        * Quality of the `description`.
        * Clarity of `course_time` (prefer courses with a clear time estimate).
    5.  **Output:** Your output **must** be a single `FinalSynthesis` object. For each of the 6 courses, you must provide a `rank` and a `justification`.
    """

    @staticmethod
    def synthesis_user(
            user_question: str,
            google_analysis: Analysis,
            youtube_analysis: Analysis,
    ) -> str:
        """User prompt for synthesizing all analyses."""

        # Serialize the Pydantic objects to JSON strings
        google_json = google_analysis.model_dump_json(indent=2)
        youtube_json = youtube_analysis.model_dump_json(indent=2)

        return f"""User Query: {user_question}

    Here are the courses found on Google:
    {google_json}

    Here are the courses found on YouTube:
    {youtube_json}

    Please analyze both lists and provide the final ranked list of the top 3 from each, formatted as a `FinalSynthesis` object.
    """


def create_message_pair(system_prompt: str, user_prompt: str) -> list[Dict[str, Any]]:
    """
    Create a standardized message pair for LLM interactions.

    Args:
        system_prompt: The system message content
        user_prompt: The user message content

    Returns:
        List containing system and user message dictionaries
    """
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def get_youtube_analysis_messages(
        user_question: str, youtube_data: str
) -> list[Dict[str, Any]]:
    """Get messages for YouTube results analysis."""
    return create_message_pair(
        PromptTemplates.youtube_analysis_system(),
        PromptTemplates.youtube_analysis_user(user_question, youtube_data),
    )


def get_google_analysis_messages(
        user_question: str, google_data: str
) -> list[Dict[str, Any]]:
    """Get messages for Google results analysis."""
    return create_message_pair(
        PromptTemplates.google_analysis_system(),
        PromptTemplates.google_analysis_user(user_question, google_data),
    )


def get_synthesis_messages(
        user_question: str, google_analysis: Analysis, youtube_analysis: Analysis
) -> list[Dict[str, Any]]:
    """Get messages for final synthesis."""
    return create_message_pair(
        PromptTemplates.synthesis_system(),
        PromptTemplates.synthesis_user(
            user_question, google_analysis, youtube_analysis,
        ),
    )
