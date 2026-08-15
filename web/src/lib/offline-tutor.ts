import type { LearnerModel, TutorTurnResponse, PedagogyMove, AffectState } from "./types";

/** Deterministic tutoring loop when no API key — still demoable for YC. */

function interestProblem(learner: LearnerModel, level: "easy" | "hard") {
  const thing = learner.interest || "cricket";
  if (level === "easy") {
    return {
      text: `Quick story: You have 3 ${thing} stickers. A friend gives you 2 more. How many ${thing} stickers do you have now?`,
      answer: 5,
    };
  }
  return {
    text: `Story time: A ${thing} club has 4 boxes. Each box has 3 balls. How many balls in all? (You can draw boxes if you want.)`,
    answer: 12,
  };
}

function extractNumber(text: string): number | null {
  const m = text.match(/-?\d+/);
  return m ? Number(m[0]) : null;
}

function looksAfraid(text: string) {
  return /idk|i don't know|dont know|stupid|can't|cannot|hard|scared|hate/i.test(text);
}

function looksBored(text: string) {
  return /boring|whatever|idc|don't care|easy peasy|too easy/i.test(text);
}

export function offlineTutorTurn(
  learner: LearnerModel,
  childMessage: string,
  turnIndex: number,
): TutorTurnResponse {
  const msg = childMessage.trim();
  const lower = msg.toLowerCase();
  const hard = learner.sessionCount > 0 || learner.whatClicked.length > 0;
  const problem = interestProblem(learner, hard ? "hard" : "easy");

  if (turnIndex === 0 || /^(hi|hello|hey|start|ready)\b/i.test(msg)) {
    return {
      reply: `Hey ${learner.name}! I'm glad you're here. We'll do a tiny ${learner.interest} story - reading + numbers together. No rush. Ready?`,
      move: "diagnose",
      affect: "engaged",
      modelPatch: {
        lastProblem: problem.text,
        skillFocus: "word-problem",
        notes: "Opened with trust + interest hook.",
      },
      problemPrompt: problem.text,
      isCorrect: null,
    };
  }

  if (looksAfraid(msg)) {
    return {
      reply: `Thanks for telling me. You're not behind - this just needs a smaller step. Forget the whole story for a second: what is 3 + 2?`,
      move: "retreat",
      affect: "afraid",
      modelPatch: {
        affect: "afraid",
        whatStuck: unique([...learner.whatStuck, "freezes when problem feels big"]),
        preferredExplanations: unique([
          ...learner.preferredExplanations,
          "break into tiny steps",
        ]),
        notes: "Repaired trust; retreated to 3+2.",
        lastProblem: "What is 3 + 2?",
      },
      problemPrompt: "What is 3 + 2?",
      isCorrect: null,
    };
  }

  if (looksBored(msg)) {
    return {
      reply: `Okay - let's make it spicier. Same idea, ${learner.interest} style: ${problem.text}`,
      move: "reframe",
      affect: "bored",
      modelPatch: {
        affect: "bored",
        preferredExplanations: unique([
          ...learner.preferredExplanations,
          "interest-tied challenge",
        ]),
        lastProblem: problem.text,
      },
      problemPrompt: problem.text,
      isCorrect: null,
    };
  }

  const n = extractNumber(msg);
  const expected =
    learner.lastProblem?.includes("3 + 2") || learner.lastProblem?.includes("3+2")
      ? 5
      : hard
        ? 12
        : 5;

  // If we just asked the full problem and they answer
  if (n !== null) {
    if (n === expected || (expected === 12 && n === 12) || (expected === 5 && n === 5)) {
      return {
        reply: `Yes - ${n} is right. You read the story and found the numbers. That was real thinking. Want one more, a little tougher?`,
        move: "celebrate",
        affect: "proud",
        modelPatch: {
          affect: "proud",
          whatClicked: unique([
            ...learner.whatClicked,
            hard ? "grouping / equal groups" : "join / addition in a story",
          ]),
          preferredExplanations: unique([
            ...learner.preferredExplanations,
            `${learner.interest} stories`,
          ]),
          notes: "Independent success. Raise difficulty next session.",
          skillFocus: "arithmetic",
        },
        isCorrect: true,
        sessionComplete: turnIndex >= 4,
      };
    }

    // Wrong number — diagnose misconception
    const move: PedagogyMove = turnIndex >= 3 ? "reframe" : "scaffold";
    const affect: AffectState = "confused";
    if (move === "reframe") {
      return {
        reply: `I see how you got ${n}. Let's draw it: three ${learner.interest} stickers, then two more join them. Count with your finger: 1-2-3, then 4-5. What number lands at the end?`,
        move: "reframe",
        affect,
        modelPatch: {
          affect,
          misconceptions: unique([
            ...learner.misconceptions,
            n > expected
              ? "may be adding an extra number from the story"
              : "may be stopping before joining both groups",
          ]),
          whatStuck: unique([...learner.whatStuck, "story addition"]),
          preferredExplanations: unique([
            ...learner.preferredExplanations,
            "draw and count",
          ]),
          lastProblem: problem.text,
          notes: `Wrong answer ${n}; reframed with drawing.`,
        },
        problemPrompt: problem.text,
        isCorrect: false,
      };
    }

    return {
      reply: `Close - ${n} is a real try. Let's scaffold: first number in the story, then the second, then join. What are the two numbers we join?`,
      move: "scaffold",
      affect,
      modelPatch: {
        affect,
        misconceptions: unique([...learner.misconceptions, `answered ${n} too early`]),
        whatStuck: unique([...learner.whatStuck, "extracting numbers from text"]),
        lastProblem: problem.text,
        notes: "Scaffold: identify the two addends before computing.",
      },
      problemPrompt: problem.text,
      isCorrect: false,
    };
  }

  if (/ready|yes|ok|okay|sure|yeah/i.test(lower)) {
    return {
      reply: problem.text,
      move: "check",
      affect: "engaged",
      modelPatch: {
        lastProblem: problem.text,
        skillFocus: "word-problem",
        affect: "engaged",
      },
      problemPrompt: problem.text,
      isCorrect: null,
    };
  }

  return {
    reply: `I'm listening. Tell me a number guess, or say "I don't know" - both are brave. Here's the story again: ${learner.lastProblem || problem.text}`,
    move: "hint",
    affect: "unknown",
    modelPatch: {
      lastProblem: learner.lastProblem || problem.text,
    },
    problemPrompt: learner.lastProblem || problem.text,
    isCorrect: null,
  };
}

function unique(items: string[]) {
  return [...new Set(items.filter(Boolean))].slice(-8);
}