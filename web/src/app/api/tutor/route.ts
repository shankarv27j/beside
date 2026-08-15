import { NextResponse } from "next/server";
import OpenAI from "openai";
import { z } from "zod";
import { offlineTutorTurn } from "@/lib/offline-tutor";
import { buildSystemPrompt, buildUserPayload } from "@/lib/tutor-prompt";
import type { ChatMessage, LearnerModel, TutorTurnResponse } from "@/lib/types";

const BodySchema = z.object({
  learner: z.custom<LearnerModel>(),
  messages: z.array(z.custom<ChatMessage>()),
  childMessage: z.string().min(1).max(2000),
  forceOffline: z.boolean().optional(),
});

const TurnSchema = z.object({
  reply: z.string(),
  move: z.enum([
    "diagnose",
    "hint",
    "scaffold",
    "reframe",
    "celebrate",
    "retreat",
    "check",
  ]),
  affect: z.enum([
    "engaged",
    "confused",
    "bored",
    "afraid",
    "proud",
    "unknown",
  ]),
  modelPatch: z
    .object({
      misconceptions: z.array(z.string()).optional(),
      whatClicked: z.array(z.string()).optional(),
      whatStuck: z.array(z.string()).optional(),
      preferredExplanations: z.array(z.string()).optional(),
      lastProblem: z.string().optional(),
      notes: z.string().optional(),
      affect: z
        .enum(["engaged", "confused", "bored", "afraid", "proud", "unknown"])
        .optional(),
      skillFocus: z
        .enum(["reading", "writing", "arithmetic", "word-problem"])
        .optional(),
    })
    .optional()
    .default({}),
  problemPrompt: z.string().optional(),
  isCorrect: z.boolean().nullable().optional(),
  sessionComplete: z.boolean().optional(),
});

export async function POST(req: Request) {
  try {
    const body = BodySchema.parse(await req.json());
    const turnIndex = body.messages.filter((m) => m.role === "child").length;
    const apiKey = process.env.OPENAI_API_KEY;

    if (!apiKey || body.forceOffline) {
      const turn = offlineTutorTurn(body.learner, body.childMessage, turnIndex);
      return NextResponse.json({ ...turn, mode: "offline" satisfies string });
    }

    const client = new OpenAI({ apiKey });
    const completion = await client.chat.completions.create({
      model: process.env.OPENAI_MODEL || "gpt-4o-mini",
      temperature: 0.6,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: buildSystemPrompt(body.learner) },
        {
          role: "user",
          content: buildUserPayload(
            body.learner,
            body.messages,
            body.childMessage,
          ),
        },
      ],
    });

    const raw = completion.choices[0]?.message?.content || "{}";
    const parsed = TurnSchema.parse(JSON.parse(raw)) as TutorTurnResponse;
    return NextResponse.json({ ...parsed, mode: "openai" });
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      {
        error: err instanceof Error ? err.message : "Tutor turn failed",
      },
      { status: 400 },
    );
  }
}