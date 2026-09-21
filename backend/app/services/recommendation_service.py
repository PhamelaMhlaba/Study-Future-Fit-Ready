from typing import List, Tuple

from app.schemas.recommendation import (
    StudyChallenge,
    StudyMethod,
    StudentContext,
    MethodRecommendation,
)


# Core mapping: primary challenge -> methods known to address it, in priority order
CHALLENGE_METHOD_MAP: dict[StudyChallenge, List[StudyMethod]] = {
    StudyChallenge.REMEMBERING: [
        StudyMethod.ACTIVE_RECALL,
        StudyMethod.SPACED_REPETITION,
    ],
    StudyChallenge.UNDERSTANDING: [
        StudyMethod.FEYNMAN_TECHNIQUE,
        StudyMethod.SELF_EXPLANATION,
        StudyMethod.ELABORATIVE_INTERROGATION,
    ],
    StudyChallenge.FOCUS: [
        StudyMethod.POMODORO,
    ],
    StudyChallenge.PROCRASTINATION: [
        StudyMethod.POMODORO,
        StudyMethod.ACTIVE_RECALL,
    ],
    StudyChallenge.KNOWING_WHAT: [
        StudyMethod.PRACTICE_TESTING,
        StudyMethod.ACTIVE_RECALL,
    ],
    StudyChallenge.TEST_PREP: [
        StudyMethod.PRACTICE_TESTING,
        StudyMethod.SPACED_REPETITION,
    ],
    StudyChallenge.MULTI_SUBJECT: [
        StudyMethod.INTERLEAVING,
    ],
    StudyChallenge.CONSISTENCY: [
        StudyMethod.SPACED_REPETITION,
        StudyMethod.POMODORO,
    ],
}


def recommend_study_methods(context: StudentContext) -> MethodRecommendation:
    methods: List[StudyMethod] = list(CHALLENGE_METHOD_MAP[context.primary_challenge])
    reasons: List[str] = [
        f"Primary challenge is '{context.primary_challenge.value}', "
        f"which {_method_names(methods)} directly address."
    ]
    confidence = 0.6  # baseline for a challenge-only match

    # Signal: forgets over time -> spaced repetition, even if not already picked
    if context.forgets_over_time and StudyMethod.SPACED_REPETITION not in methods:
        methods.append(StudyMethod.SPACED_REPETITION)
        reasons.append(
            "Scores drop days after studying, which spaced repetition is designed to fix."
        )
        confidence += 0.1

    # Signal: strong on single topics, weak on mixed tests -> interleaving
    if context.strong_on_single_topics and StudyMethod.INTERLEAVING not in methods:
        methods.append(StudyMethod.INTERLEAVING)
        reasons.append(
            "Strong on isolated topics but weaker on mixed material — interleaving builds "
            "the ability to distinguish between topics under test conditions."
        )
        confidence += 0.1

    # Signal: declining quiz score trend -> prioritise active recall + practice testing
    if _is_declining(context.recent_quiz_scores):
        for m in (StudyMethod.ACTIVE_RECALL, StudyMethod.PRACTICE_TESTING):
            if m not in methods:
                methods.append(m)
        reasons.append("Recent quiz scores show a declining trend — recall-based methods correct this fastest.")
        confidence += 0.1

    # Signal: low confidence -> lead with lower-stakes methods, deprioritise cold testing
    if context.confidence_level == "low":
        reasons.append("Confidence is low, so self-explanation is prioritised before practice testing.")
        methods = _reorder_low_confidence(methods)

    # Constraint: limited time before assessment -> trim to top 2, weighted toward practice testing
    if context.days_until_assessment is not None and context.days_until_assessment <= 3:
        methods = _prioritise_for_time_pressure(methods)
        reasons.append(f"Only {context.days_until_assessment} day(s) left — narrowed to the highest-yield methods.")

    # Constraint: short session length -> drop methods that need long blocks (Feynman, dual coding)
    if context.minutes_available is not None and context.minutes_available < 20:
        methods = [m for m in methods if m not in (StudyMethod.FEYNMAN_TECHNIQUE, StudyMethod.DUAL_CODING)]
        reasons.append("Session is short, so time-intensive methods were dropped in favour of quick ones.")

    methods = _dedupe_preserve_order(methods)[:3]  # cap at 3 so it stays actionable
    confidence = min(confidence, 1.0)

    return MethodRecommendation(
        methods=methods,
        reasoning=" ".join(reasons),
        confidence=round(confidence, 2),
    )


# --- helpers -------------------------------------------------------------

def _method_names(methods: List[StudyMethod]) -> str:
    return " and ".join(m.value.replace("_", " ") for m in methods)


def _is_declining(scores: List[float], lookback: int = 3) -> bool:
    if len(scores) < 2:
        return False
    recent = scores[-lookback:]
    return recent == sorted(recent, reverse=True) and recent[0] > recent[-1]


def _reorder_low_confidence(methods: List[StudyMethod]) -> List[StudyMethod]:
    priority = [StudyMethod.SELF_EXPLANATION, StudyMethod.ELABORATIVE_INTERROGATION]
    front = [m for m in priority if m in methods]
    rest = [m for m in methods if m not in front]
    return front + rest


def _prioritise_for_time_pressure(methods: List[StudyMethod]) -> List[StudyMethod]:
    priority = [StudyMethod.PRACTICE_TESTING, StudyMethod.ACTIVE_RECALL]
    front = [m for m in priority if m in methods]
    rest = [m for m in methods if m not in front]
    return (front + rest)[:2]


def _dedupe_preserve_order(methods: List[StudyMethod]) -> List[StudyMethod]:
    seen = set()
    out = []
    for m in methods:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out