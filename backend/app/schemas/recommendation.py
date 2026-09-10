from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class StudyMethod(str, Enum):
    ACTIVE_RECALL = "active_recall"
    SPACED_REPETITION = "spaced_repetition"
    PRACTICE_TESTING = "practice_testing"
    INTERLEAVING = "interleaving"
    ELABORATIVE_INTERROGATION = "elaborative_interrogation"
    DUAL_CODING = "dual_coding"
    SELF_EXPLANATION = "self_explanation"
    FEYNMAN_TECHNIQUE = "feynman_technique"
    POMODORO = "pomodoro"


class StudyChallenge(str, Enum):
    REMEMBERING = "remembering_information"
    UNDERSTANDING = "understanding_concepts"
    FOCUS = "staying_focused"
    PROCRASTINATION = "procrastination"
    KNOWING_WHAT = "knowing_what_to_study"
    TEST_PREP = "preparing_for_tests"
    MULTI_SUBJECT = "managing_multiple_subjects"
    CONSISTENCY = "staying_consistent"


class StudentContext(BaseModel):
    """Signals pulled from the student's profile, habits and history.
    In production this gets assembled server-side from DB records —
    the student never sends this directly.
    """
    student_id: str
    subject: str
    topic: Optional[str] = None
    primary_challenge: StudyChallenge
    last_method_used: Optional[str] = None  # a StudyMethod value OR a raw habit like "reread_notes"
    recent_quiz_scores: List[float] = Field(default_factory=list)  # chronological, most recent last
    forgets_over_time: bool = False          # scores well right after studying, poorly days later
    strong_on_single_topics: bool = False    # good on isolated topics, weak on mixed/cumulative tests
    confidence_level: Optional[str] = None   # "low" | "medium" | "high"
    days_until_assessment: Optional[int] = None
    minutes_available: Optional[int] = None


class MethodRecommendation(BaseModel):
    methods: List[StudyMethod]
    reasoning: str
    confidence: float = Field(ge=0, le=1)