from crewai import Agent, Task


def build_tasks(agents: dict[str, Agent]) -> list[Task]:
    observe = Task(
        description=(
            "Diagnose the child's state for this turn.\n\n"
            "Child name: {child_name}\n"
            "Age: {age}\n"
            "Skill focus: {skill}\n"
            "Known profile: {profile}\n"
            "Recent history:\n{history}\n"
            "Child just said: {child_message}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"affect":"confused|scared|bored|engaged|proud|unknown",'
            '"evidence":"short reason"}}'
        ),
        expected_output='JSON object with keys affect and evidence',
        agent=agents["observer"],
    )

    strategize = Task(
        description=(
            "Using the Observer result, choose exactly one pedagogy move "
            "and one micro-goal for reading/writing/arithmetic.\n\n"
            "Child name: {child_name}\n"
            "Age: {age}\n"
            "Skill focus: {skill}\n"
            "Child just said: {child_message}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"move":"diagnose|hint|scaffold|reframe|retreat|celebrate|check",'
            '"reason":"short",'
            '"micro_goal":"one tiny next step"}}'
        ),
        expected_output='JSON object with keys move, reason, micro_goal',
        agent=agents["strategist"],
        context=[observe],
    )

    tutor = Task(
        description=(
            "Write what the child should hear this turn.\n"
            "Follow the Strategist move and micro_goal. Keep it short and warm.\n\n"
            "Child name: {child_name}\n"
            "Age: {age}\n"
            "Interest / context: {interest}\n"
            "Child just said: {child_message}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"reply":"text the child will see"}}'
        ),
        expected_output='JSON object with key reply',
        agent=agents["tutor"],
        context=[observe, strategize],
    )

    memory = Task(
        description=(
            "Propose profile updates from this turn for long-term memory.\n\n"
            "Child name: {child_name}\n"
            "Existing profile: {profile}\n\n"
            "Return ONLY valid JSON:\n"
            '{{"what_clicked":["..."],'
            '"what_stuck":["..."],'
            '"misconceptions":["..."],'
            '"notes":"one sentence"}}'
        ),
        expected_output='JSON object with memory update fields',
        agent=agents["memory_writer"],
        context=[observe, strategize, tutor],
    )

    return [observe, strategize, tutor, memory]