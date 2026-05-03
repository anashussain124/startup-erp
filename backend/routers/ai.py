from auth.dependencies import get_current_user
from services.ai_service import query_ai_with_context
from services.billing_service import check_billing_limits, increment_usage
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["Intelligence"])

class AIQuery(BaseModel):
    query: str

from services.ai_service import query_ai_with_context, generate_actionable_suggestion
from services.insight_service import create_insight

@router.post("/query")
def ask_ai(
    data: AIQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Query the AI, with billing enforcement and proactive actionable suggestions."""
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")
        
    # 1. Billing Check
    check_billing_limits(db, current_user.company_id, "ai_query")

    # 2. Process Query
    answer = query_ai_with_context(data.query, current_user.company_id, db)
    
    # 3. Generate Proactive Action Item
    suggestion = generate_actionable_suggestion(answer, data.query)
    create_insight(
        db, 
        current_user.company_id, 
        "query", 
        f"Suggestion for: {data.query[:30]}...", 
        suggestion['advice'],
        action=f"Follow-up on {suggestion['category']}"
    )

    # 4. Track Usage
    increment_usage(db, current_user.company_id, "ai_query")
    
    return {"answer": answer, "suggestion": suggestion['advice']}
