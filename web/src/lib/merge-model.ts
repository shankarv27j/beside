import type { LearnerModel, TutorTurnResponse } from "./types";

export function applyModelPatch(
  learner: LearnerModel,
  turn: TutorTurnResponse,
): LearnerModel {
  const patch = turn.modelPatch || {};
  const mergeList = (current: string[], next?: string[]) => {
    if (!next) return current;
    return [...new Set([...current, ...next])].slice(-10);
  };

  return {
    ...learner,
    updatedAt: new Date().toISOString(),
    affect: patch.affect ?? turn.affect ?? learner.affect,
    skillFocus: patch.skillFocus ?? learner.skillFocus,
    misconceptions: mergeList(learner.misconceptions, patch.misconceptions),
    whatClicked: mergeList(learner.whatClicked, patch.whatClicked),
    whatStuck: mergeList(learner.whatStuck, patch.whatStuck),
    preferredExplanations: mergeList(
      learner.preferredExplanations,
      patch.preferredExplanations,
    ),
    lastProblem: patch.lastProblem ?? turn.problemPrompt ?? learner.lastProblem,
    notes: patch.notes ?? learner.notes,
  };
}