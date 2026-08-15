export type AffectState = "engaged" | "confused" | "bored" | "afraid" | "proud" | "unknown";

export type PedagogyMove =
  | "diagnose"
  | "hint"
  | "scaffold"
  | "reframe"
  | "celebrate"
  | "retreat"
  | "check";

export type SkillFocus = "reading" | "writing" | "arithmetic" | "word-problem";

export interface LearnerModel {
  id: string;
  name: string;
  age: number;
  interest: string;
  createdAt: string;
  updatedAt: string;
  sessionCount: number;
  skillFocus: SkillFocus;
  affect: AffectState;
  misconceptions: string[];
  whatClicked: string[];
  whatStuck: string[];
  preferredExplanations: string[];
  lastProblem?: string;
  notes: string;
}

export interface ChatMessage {
  id: string;
  role: "tutor" | "child" | "system";
  content: string;
  move?: PedagogyMove;
  affect?: AffectState;
  at: string;
}

export interface TutorTurnResponse {
  reply: string;
  move: PedagogyMove;
  affect: AffectState;
  modelPatch: Partial<
    Pick<
      LearnerModel,
      | "misconceptions"
      | "whatClicked"
      | "whatStuck"
      | "preferredExplanations"
      | "lastProblem"
      | "notes"
      | "affect"
      | "skillFocus"
    >
  >;
  problemPrompt?: string;
  isCorrect?: boolean | null;
  sessionComplete?: boolean;
}

export interface SessionState {
  learnerId: string;
  messages: ChatMessage[];
  startedAt: string;
}