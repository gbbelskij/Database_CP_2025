from typing import List
from fastapi import APIRouter, Depends
from app.schemas import RuleCreate, RuleRead
from app.deps import get_current_user
from app.sql import queries

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=RuleRead, summary="Создать правило автоматики")
def create_rule(rule_in: RuleCreate, user: dict = Depends(get_current_user)):
    rule = queries.create_rule(
        home_id=rule_in.home_id,
        condition=rule_in.condition,
        action=rule_in.action,
    )
    queries.create_log(user["id"], f"Created rule in home {rule_in.home_id}")
    return rule


@router.get("/home/{home_id}", response_model=List[RuleRead], summary="Правила дома")
def list_rules(home_id: int, user: dict = Depends(get_current_user)):
    return queries.get_rules_by_home(home_id)


@router.delete("/{rule_id}", summary="Удалить правило")
def delete_rule(rule_id: int, user: dict = Depends(get_current_user)):
    queries.delete_rule(rule_id)
    queries.create_log(user["id"], f"Deleted rule {rule_id}")
    return {"detail": "Rule deleted"}
