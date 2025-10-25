from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Annotated, List , Optional
from langgraph.graph.message import add_messages


class OutputStructure(BaseModel):
    course_name: str = Field(
        description="The exact name of the course.",
    )
    website_name: str = Field(
        ...,
        description="The name of the website hosting the course (e.g., Coursera, Udemy,Youtube)."
    )
    free_course: Optional[bool] = Field(
        None,  # This sets the default value to None
        description="True if the course is free, False if paid, None if not specified."
    )
    course_time: Optional[str] = Field(
        None,
        description="The estimated time to complete the course (e.g., '10 hours', '3 weeks')."
    )
    course_topics: List[str] = Field(
        ...,  # This is argument 1 (marks it as required)
        description="A list of key topics or modules covered in the course."

    )
    description: str = Field(
        ...,
        description="A brief summary of the course content.",
    )


class Analysis(BaseModel):
    """
    A model to hold the list of extracted courses from a data source
    (like Google or YouTube).
    """
    courses: List[OutputStructure] = Field(
        description="A list of all the courses found in the analysis."
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_question: str | None
    google_results: str | None
    youtube_urls: List[str] | None
    youtube_results: str | None
    google_analysis: Optional[Analysis]  # This is now a Pydantic model holding a list
    youtube_analysis: Optional[Analysis]
    final_answer: str | None


class RankedCourse(OutputStructure):
    """
    Extends the basic course structure to include rank and justification
    for the final synthesis.
    """
    rank: int = Field(
        ...,
        description="The final rank of the course (1 is best, 6 is worst)."
    )
    justification: str = Field(
        ...,
        description="A  (5-6 sentence) justification for why this course "
                    "was selected and ranked."
    )

class FinalSynthesis(BaseModel):
    """
    The final output model, containing a single ranked list of the
    top 6 courses.
    """
    # This list will contain RankedCourse objects,
    # each one having all the course data plus rank/justification.
    ranked_courses: List[RankedCourse] = Field(
        description="The final list of the 6 best courses, ranked 1-6."
    )


