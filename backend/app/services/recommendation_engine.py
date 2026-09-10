"""Rule-based adaptive recommendation engine.

Each rule inspects the student's context and returns a MethodRecommendation
(or None if it doesn't apply). We evaluate every rule and return the one
with the highest confidence, rather than the first match — this keeps the
engine easy to extend without earlier rules silently shadowing later ones.

Recommendations returned here should be persisted (student_id, context
snapshot, methods, reasoning, timestamp) so outcomes can be tracked and
used to refine confidence scores over time — that's the "record
recommendations and outcomes" requirement from the spec.
"""
from typing import Callable, List, Optional

from app.schemas.recommendation import (
    MethodRecommendation,
    StudentContext,
    StudyChallenge,
    StudyMethod,
)

Rule = Callable[[StudentContext], Optional[MethodRecommendation]]
RULES: List[Rule] = []


def rule(fn: Rule) -> Rule:
    RULES.append(fn)
    return fn


@rule
def passive_reading_poor_scores(ctx: StudentContext) -> Optional[MethodRecommendation]:
    low_scores = [s for s in ctx.recent_quiz_scores if s < 60]
    if ctx.last_method_used in (None, "reread_notes", "highlighting") and len(low_scores) >= 2:
        return MethodRecommendation(
            methods=[StudyMethod.ACTIVE_RECALL, StudyMethod.PRACTICE_TESTING],
            reasoning=(
                "Your recent scores suggest re-reading or highlighting isn't translating "
                "into recall under test conditions. Switching to retrieval-based methods may help."
            ),
            confidence=0.85,
        )
    return None


@rule
def forgets_over_time(ctx: StudentContext) -> Optional[MethodRecommendation]:
    if ctx.forgets_over_time:
        return MethodRecommendation(
            methods=[StudyMethod.SPACED_REPETITION],
            reasoning=(
                "You understand the material initially but it fades over days. Spacing "
                "reviews out over time tends to improve long-term retention."
            ),
            confidence=0.80,
        )
    return None


@rule
def strong_individually_weak_mixed(ctx: StudentContext) -> Optional[MethodRecommendation]:
    if ctx.strong_on_single_topics:
        return MethodRecommendation(
            methods=[StudyMethod.INTERLEAVING, StudyMethod.PRACTICE_TESTING],
            reasoning=(
                "You perform well on topics in isolation but struggle when they're mixed "
                "together, like in a real exam. Interleaving practice across topics builds "
                "that switching skill."
            ),
            confidence=0.80,
        )
    return None


@rule
def low_confidence_near_assessment(ctx: StudentContext) -> Optional[MethodRecommendation]:
    if ctx.confidence_level == "low" and ctx.days_until_assessment is not None and ctx.days_until_assessment <= 7:
        return MethodRecommendation(
            methods=[StudyMethod.PRACTICE_TESTING, StudyMethod.SELF_EXPLANATION],
            reasoning=(
                "Your assessment is close and confidence is low. Practice testing under "
                "timed conditions, paired with explaining your reasoning, builds both skill "
                "and confidence quickly."
            ),
            confidence=0.75,
        )
    return None


@rule
def understanding_challenge(ctx: StudentContext) -> Optional[MethodRecommendation]:
    if ctx.primary_challenge == StudyChallenge.UNDERSTANDING:
        return MethodRecommendation(
            methods=[StudyMethod.FEYNMAN_TECHNIQUE, StudyMethod.ELABORATIVE_INTERROGATION],
            reasoning=(
                "You've flagged understanding difficult concepts as your main challenge. "
                "Explaining ideas in simple terms and asking 'why' questions helps surface "
                "gaps in understanding."
            ),
            confidence=0.60,
        )
    return None


@rule
def focus_challenge(ctx: StudentContext) -> Optional[MethodRecommendation]:
    if ctx.primary_challenge == StudyChallenge.FOCUS:
        return MethodRecommendation(
            methods=[StudyMethod.POMODORO],
            reasoning=(
                "Staying focused is your main challenge, so structuring sessions into "
                "short, timed intervals with breaks may help more than longer unstructured sessions."
            ),
            confidence=0.55,
        )
    return None


DEFAULT_RECOMMENDATION = MethodRecommendation(
    methods=[StudyMethod.ACTIVE_RECALL, StudyMethod.SPACED_REPETITION],
    reasoning=(
        "Based on your answers, these general-purpose strategies are a strong starting "
        "point while we gather more data on what works for you."
    ),
    confidence=0.30,
)


def generate_recommendation(ctx: StudentContext) -> MethodRecommendation:
    """Evaluate all rules and return the highest-confidence match, or the default."""
    candidates = [c for c in (r(ctx) for r in RULES) if c is not None]
    if not candidates:
        return DEFAULT_RECOMMENDATION
    return max(candidates, key=lambda c: c.confidence)