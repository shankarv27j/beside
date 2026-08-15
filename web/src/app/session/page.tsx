"use client";

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { LearnerModelPanel } from "@/components/LearnerModelPanel";
import { DEMO_CAPTIONS, DEMO_CHILD_LINES } from "@/lib/demo-script";
import { applyModelPatch } from "@/lib/merge-model";
import {
  getLearner,
  getSession,
  saveSession,
  upsertLearner,
} from "@/lib/storage";
import type {
  ChatMessage,
  LearnerModel,
  PedagogyMove,
  TutorTurnResponse,
} from "@/lib/types";

function SessionInner() {
  const params = useSearchParams();
  const learnerId = params.get("id") || "";
  const autoDemo = params.get("demo") === "1";

  const [learner, setLearner] = useState<LearnerModel | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [lastMove, setLastMove] = useState<PedagogyMove | undefined>();
  const [demoStep, setDemoStep] = useState(0);
  const [demoCaption, setDemoCaption] = useState("");
  const [mode, setMode] = useState<string>("");
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const l = getLearner(learnerId);
    if (!l) return;
    setLearner(l);
    if (autoDemo) {
      saveSession(null);
      setMessages([]);
      setDemoStep(0);
      started.current = false;
      return;
    }
    const existing = getSession();
    if (existing && existing.learnerId === learnerId && existing.messages.length) {
      setMessages(existing.messages);
      const lastTutor = [...existing.messages].reverse().find((m) => m.role === "tutor");
      setLastMove(lastTutor?.move);
    }
  }, [autoDemo, learnerId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const persist = useCallback(
    (nextLearner: LearnerModel, nextMessages: ChatMessage[]) => {
      upsertLearner(nextLearner);
      setLearner(nextLearner);
      setMessages(nextMessages);
      saveSession({
        learnerId: nextLearner.id,
        messages: nextMessages,
        startedAt: nextMessages[0]?.at || new Date().toISOString(),
      });
    },
    [],
  );

  const send = useCallback(
    async (text: string) => {
      if (!learner || !text.trim() || busy) return;
      setBusy(true);
      setError("");
      const childMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "child",
        content: text.trim(),
        at: new Date().toISOString(),
      };
      const withChild = [...messages, childMsg];
      setMessages(withChild);

      try {
        const res = await fetch("/api/tutor", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            learner,
            messages,
            childMessage: text.trim(),
          }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Tutor failed");

        const turn = data as TutorTurnResponse & { mode?: string };
        setMode(turn.mode || "");
        setLastMove(turn.move);

        const tutorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "tutor",
          content: turn.reply,
          move: turn.move,
          affect: turn.affect,
          at: new Date().toISOString(),
        };
        let nextMessages = [...withChild, tutorMsg];
        if (turn.problemPrompt && !turn.reply.includes(turn.problemPrompt)) {
          nextMessages = [
            ...nextMessages,
            {
              id: crypto.randomUUID(),
              role: "tutor",
              content: turn.problemPrompt,
              move: "check",
              at: new Date().toISOString(),
            },
          ];
        }

        let nextLearner = applyModelPatch(learner, turn);
        if (turn.sessionComplete) {
          nextLearner = {
            ...nextLearner,
            sessionCount: nextLearner.sessionCount + 1,
            notes: `${nextLearner.notes} Session complete.`,
          };
        }
        persist(nextLearner, nextMessages);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Something went wrong");
        setMessages(withChild);
      } finally {
        setBusy(false);
        setInput("");
      }
    },
    [busy, learner, messages, persist],
  );

  const begin = useCallback(async () => {
    if (!learner || started.current || messages.length || autoDemo) return;
    started.current = true;
    await send("hi");
  }, [autoDemo, learner, messages.length, send]);

  useEffect(() => {
    if (learner && !messages.length && !autoDemo) void begin();
  }, [autoDemo, learner, messages.length, begin]);

  useEffect(() => {
    if (!autoDemo || !learner || busy) return;
    if (demoStep >= DEMO_CHILD_LINES.length) return;

    const childTurns = messages.filter((m) => m.role === "child").length;
    if (childTurns !== demoStep) return;
    if (demoStep > 0) {
      const tutorTurns = messages.filter((m) => m.role === "tutor").length;
      if (tutorTurns < demoStep) return;
    }

    const t = setTimeout(() => {
      setDemoCaption(DEMO_CAPTIONS[demoStep] || "");
      void send(DEMO_CHILD_LINES[demoStep]);
      setDemoStep((s) => s + 1);
    }, demoStep === 0 ? 700 : 1700);
    return () => clearTimeout(t);
  }, [autoDemo, busy, demoStep, learner, messages, send]);

  const status = useMemo(() => {
    if (mode === "openai") return "Live model";
    if (mode === "offline") return "Offline tutor loop";
    return "Connecting…";
  }, [mode]);

  if (!learnerId) {
    return (
      <main className="shell">
        <p>Missing learner. <Link href="/">Go home</Link></p>
      </main>
    );
  }

  if (!learner) {
    return (
      <main className="shell">
        <p>Learner not found. <Link href="/">Create one</Link></p>
      </main>
    );
  }

  return (
    <main className="shell session-shell">
      <header className="topbar">
        <div>
          <Link href="/" className="brand">
            Primerycomb
          </Link>
          <p className="muted tiny">{status} · Mentoring loop</p>
        </div>
        <nav className="nav">
          <Link href={`/parent?id=${learner.id}`}>Parent view</Link>
          <Link href={`/session?id=${learner.id}&demo=1`}>Demo Play</Link>
        </nav>
      </header>

      {demoCaption ? <div className="demo-caption">{demoCaption}</div> : null}

      <div className="session-grid">
        <section className="panel chat-panel">
          <p className="eyebrow">Session</p>
          <h1>Tutor ↔ {learner.name}</h1>
          <div className="transcript" aria-live="polite">
            {messages.map((m) => (
              <article
                key={m.id}
                className={`bubble ${m.role}${m.move ? ` move-${m.move}` : ""}`}
              >
                <header>
                  <span>{m.role === "tutor" ? "Tutor" : "Child"}</span>
                  {m.move ? <span className="tag">{m.move}</span> : null}
                </header>
                <p>{m.content}</p>
              </article>
            ))}
            {busy ? <p className="muted">Tutor is thinking…</p> : null}
            <div ref={bottomRef} />
          </div>

          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              void send(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Reply as ${learner.name}…`}
              disabled={busy || autoDemo}
              aria-label="Child reply"
            />
            <button type="submit" disabled={busy || !input.trim() || autoDemo}>
              Send
            </button>
          </form>
          {error ? <p className="error">{error}</p> : null}
          <p className="muted tiny">
            Tip: try a wrong number, then “I don’t know”, then the right answer — watch
            the moves change.
          </p>
        </section>

        <LearnerModelPanel
          learner={learner}
          lastMove={lastMove}
          lastAffect={learner.affect}
        />
      </div>
    </main>
  );
}

export default function SessionPage() {
  return (
    <Suspense fallback={<main className="shell">Loading session…</main>}>
      <SessionInner />
    </Suspense>
  );
}