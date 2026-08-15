import json
from datetime import datetime

from sqlmodel import Session, select

from app.crew import run_mentor_turn
from app.memory import history_blob, merge_memory, profile_blob
from app.models import Child, Turn, TutorSession


def list_children(db: Session) -> list[Child]:
    return list(db.exec(select(Child).order_by(Child.updated_at.desc())).all())


def get_child(db: Session, child_id: str) -> Child | None:
    return db.get(Child, child_id)


def create_child(
    db: Session,
    *,
    name: str,
    age: int,
    interest: str,
    skill_focus: str,
) -> Child:
    child = Child(
        name=name.strip(),
        age=age,
        interest=interest.strip() or "stories",
        skill_focus=skill_focus,
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    return child


def get_active_session(db: Session, child_id: str) -> TutorSession | None:
    return db.exec(
        select(TutorSession).where(
            TutorSession.child_id == child_id,
            TutorSession.active == True,  # noqa: E712
        )
    ).first()


def start_session(db: Session, child: Child, skill: str | None = None) -> TutorSession:
    # end any active sessions
    active = db.exec(
        select(TutorSession).where(
            TutorSession.child_id == child.id,
            TutorSession.active == True,  # noqa: E712
        )
    ).all()
    for s in active:
        s.active = False
        s.ended_at = datetime.utcnow()
        db.add(s)

    session = TutorSession(
        child_id=child.id,
        skill=skill or child.skill_focus,
    )
    child.session_count += 1
    child.updated_at = datetime.utcnow()
    db.add(session)
    db.add(child)
    db.commit()
    db.refresh(session)
    return session


def get_or_start_session(db: Session, child: Child) -> TutorSession:
    existing = get_active_session(db, child.id)
    if existing:
        return existing
    return start_session(db, child)


def get_session(db: Session, session_id: str) -> TutorSession | None:
    return db.get(TutorSession, session_id)


def list_turns(db: Session, session_id: str) -> list[Turn]:
    return list(
        db.exec(
            select(Turn)
            .where(Turn.session_id == session_id)
            .order_by(Turn.created_at)
        ).all()
    )


def process_turn(
    db: Session,
    *,
    child: Child,
    session: TutorSession,
    child_message: str,
) -> Turn:
    prior = list_turns(db, session.id)
    result = run_mentor_turn(
        child_name=child.name,
        age=child.age,
        skill=session.skill,
        interest=child.interest,
        profile=profile_blob(child),
        history=history_blob(prior),
        child_message=child_message,
    )

    memory_update = result.get("memory_update") or {}
    if isinstance(memory_update, dict):
        merge_memory(child, memory_update, result.get("affect"))

    turn = Turn(
        session_id=session.id,
        child_id=child.id,
        child_message=child_message,
        tutor_reply=str(result.get("reply") or ""),
        affect=result.get("affect"),
        move=result.get("move"),
        micro_goal=result.get("micro_goal"),
        memory_update_json=json.dumps(memory_update),
    )
    db.add(child)
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn


def rate_turn(
    db: Session,
    turn_id: str,
    rating: str,
    better_reply: str | None = None,
) -> Turn | None:
    turn = db.get(Turn, turn_id)
    if not turn:
        return None
    turn.human_rating = rating
    if better_reply:
        turn.human_better_reply = better_reply.strip()
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn