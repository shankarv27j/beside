import type { LearnerModel, SessionState } from "./types";

const LEARNERS_KEY = "primerycomb.learners";
const SESSION_KEY = "primerycomb.session";

function canUseStorage() {
  return typeof window !== "undefined" && !!window.localStorage;
}

export function listLearners(): LearnerModel[] {
  if (!canUseStorage()) return [];
  try {
    const raw = localStorage.getItem(LEARNERS_KEY);
    return raw ? (JSON.parse(raw) as LearnerModel[]) : [];
  } catch {
    return [];
  }
}

export function saveLearners(learners: LearnerModel[]) {
  if (!canUseStorage()) return;
  localStorage.setItem(LEARNERS_KEY, JSON.stringify(learners));
}

export function getLearner(id: string): LearnerModel | undefined {
  return listLearners().find((l) => l.id === id);
}

export function upsertLearner(learner: LearnerModel) {
  const all = listLearners();
  const idx = all.findIndex((l) => l.id === learner.id);
  if (idx >= 0) all[idx] = learner;
  else all.push(learner);
  saveLearners(all);
}

export function deleteLearner(id: string) {
  saveLearners(listLearners().filter((l) => l.id !== id));
}

export function getSession(): SessionState | null {
  if (!canUseStorage()) return null;
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as SessionState) : null;
  } catch {
    return null;
  }
}

export function saveSession(session: SessionState | null) {
  if (!canUseStorage()) return;
  if (!session) localStorage.removeItem(SESSION_KEY);
  else localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function createLearner(input: {
  name: string;
  age: number;
  interest: string;
}): LearnerModel {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name: input.name.trim(),
    age: input.age,
    interest: input.interest.trim() || "stories",
    createdAt: now,
    updatedAt: now,
    sessionCount: 0,
    skillFocus: "word-problem",
    affect: "unknown",
    misconceptions: [],
    whatClicked: [],
    whatStuck: [],
    preferredExplanations: [],
    notes: "New learner. Build trust first; celebrate effort.",
  };
}