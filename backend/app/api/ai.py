from fastapi import APIRouter

from app.schemas.recommendation import MethodRecommendation, StudentContext
from app.services.recommendation_engine import generate_recommendation

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/recommendation", response_model=MethodRecommendation)
def recommend(context: StudentContext) -> MethodRecommendation:
    return generate_recommendation(context)
