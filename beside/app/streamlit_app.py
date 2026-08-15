"""Beside classroom UI in Streamlit.

Run from beside/:
  .venv\\Scripts\\python.exe -m streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st
from sqlmodel import Session

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import engine, init_db
from app.services import (
    create_child,
    get_child,
    get_or_start_session,
    list_children,
    list_turns,
    process_turn,
    rate_turn,
    start_session,
)


def _lists(child):
    def load(raw: str):
        try:
            data = json.loads(raw or "[]")
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    return load(child.what_clicked), load(child.what_stuck), load(child.misconceptions)


st.set_page_config(
    page_title="Beside",
    page_icon="📘",
    layout="wide",
)

init_db()

if "page" not in st.session_state:
    st.session_state.page = "Home"

st.title("Beside")
st.caption("1:1 AI tutor that grows with each child")

page = st.sidebar.radio(
    "Go to",
    ["Home", "Classroom", "Parent view"],
    key="page",
)

with Session(engine) as db:
    children = list_children(db)

    if page == "Home":
        st.subheader("New child")
        with st.form("create_child"):
            name = st.text_input("Name", value="Asha")
            age = st.number_input("Age", min_value=8, max_value=14, value=10)
            interest = st.text_input("Interest", value="cricket")
            skill = st.selectbox(
                "Skill focus",
                ["arithmetic", "reading", "writing"],
            )
            submitted = st.form_submit_button("Create child")
            if submitted and name.strip():
                child = create_child(
                    db,
                    name=name,
                    age=int(age),
                    interest=interest,
                    skill_focus=skill,
                )
                st.session_state["child_id"] = child.id
                st.session_state.page = "Classroom"
                st.success(f"Created {child.name}. Opening classroom…")
                st.rerun()

        st.subheader("Saved children")
        if not children:
            st.info("No children yet. Create one above.")
        else:
            for c in children:
                cols = st.columns([3, 1, 1])
                cols[0].write(
                    f"**{c.name}**, {c.age} · {c.interest} · "
                    f"{c.session_count} sessions · {c.skill_focus}"
                )
                if cols[1].button("Classroom", key=f"class_{c.id}"):
                    st.session_state["child_id"] = c.id
                    st.session_state.page = "Classroom"
                    st.rerun()
                if cols[2].button("Parent", key=f"parent_{c.id}"):
                    st.session_state["child_id"] = c.id
                    st.session_state.page = "Parent view"
                    st.rerun()

    elif page == "Classroom":
        if not children:
            st.warning("Create a child on Home first.")
        else:
            options = {f"{c.name} ({c.id[:6]})": c.id for c in children}
            default_id = st.session_state.get("child_id", children[0].id)
            labels = list(options.keys())
            default_label = next(
                (k for k, v in options.items() if v == default_id),
                labels[0],
            )
            label = st.selectbox(
                "Child",
                labels,
                index=labels.index(default_label),
            )
            child_id = options[label]
            st.session_state["child_id"] = child_id
            child = get_child(db, child_id)
            assert child is not None

            if st.button("New session"):
                start_session(db, child)
                st.rerun()

            session = get_or_start_session(db, child)
            turns = list_turns(db, session.id)
            clicked, stuck, misconceptions = _lists(child)

            left, right = st.columns([1.4, 0.9])

            with left:
                st.subheader(f"Tutor ↔ {child.name}")
                st.caption(
                    f"Skill: {session.skill} · Session count: {child.session_count}"
                )

                for t in turns:
                    with st.chat_message("user"):
                        st.write(t.child_message)
                    with st.chat_message("assistant"):
                        meta = " · ".join(x for x in [t.move, t.affect] if x)
                        if meta:
                            st.caption(meta)
                        st.write(t.tutor_reply)
                        r1, r2, r3 = st.columns(3)
                        if r1.button("That's me", key=f"me_{t.id}"):
                            rate_turn(db, t.id, "me")
                            st.rerun()
                        if r2.button("Not me", key=f"not_{t.id}"):
                            rate_turn(db, t.id, "not_me")
                            st.rerun()
                        if t.human_rating:
                            r3.caption(f"Rated: {t.human_rating}")

                prompt = st.chat_input(f"Reply as {child.name}…")
                if prompt:
                    with st.spinner("Tutor is thinking… (fast mode: one model call)"):
                        try:
                            process_turn(
                                db,
                                child=child,
                                session=session,
                                child_message=prompt.strip(),
                            )
                        except Exception as exc:
                            st.error(str(exc))
                        else:
                            st.rerun()

            with right:
                st.subheader("Learner model")
                st.write(f"**{child.name}** · loves {child.interest}")
                st.metric("Affect", child.affect)
                st.metric("Sessions", child.session_count)
                st.write("**What clicked**")
                st.write(clicked or ["Not yet"])
                st.write("**What's stuck**")
                st.write(stuck or ["Nothing logged"])
                st.write("**Misconceptions**")
                st.write(misconceptions or ["None yet"])
                st.write("**Notes**")
                st.write(child.notes)

    elif page == "Parent view":
        if not children:
            st.warning("Create a child on Home first.")
        else:
            options = {f"{c.name} ({c.id[:6]})": c.id for c in children}
            default_id = st.session_state.get("child_id", children[0].id)
            labels = list(options.keys())
            default_label = next(
                (k for k, v in options.items() if v == default_id),
                labels[0],
            )
            label = st.selectbox(
                "Child",
                labels,
                index=labels.index(default_label),
                key="parent_child",
            )
            child = get_child(db, options[label])
            assert child is not None
            clicked, stuck, misconceptions = _lists(child)

            st.subheader(f"Parent view · {child.name}")
            st.caption("What a devoted tutor would tell you")
            a, b = st.columns(2)
            with a:
                st.write("**What clicked**")
                st.write(clicked or ["None yet"])
                st.write("**Misconceptions**")
                st.write(misconceptions or ["None yet"])
            with b:
                st.write("**What's stuck**")
                st.write(stuck or ["Nothing stuck"])
                st.write("**Tutor notes**")
                st.write(child.notes)
            st.caption(
                f"Sessions: {child.session_count} · Affect: {child.affect} · "
                f"Focus: {child.skill_focus}"
            )