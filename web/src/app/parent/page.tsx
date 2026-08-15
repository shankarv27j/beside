"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getLearner } from "@/lib/storage";
import type { LearnerModel } from "@/lib/types";

function ParentInner() {
  const params = useSearchParams();
  const id = params.get("id") || "";
  const [learner, setLearner] = useState<LearnerModel | null>(null);

  useEffect(() => {
    setLearner(id ? getLearner(id) || null : null);
  }, [id]);

  if (!id) {
    return (
      <main className="shell">
        <p>
          Pick a learner from <Link href="/">home</Link>.
        </p>
      </main>
    );
  }

  if (!learner) {
    return (
      <main className="shell">
        <p>
          Learner not found. <Link href="/">Home</Link>
        </p>
      </main>
    );
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <Link href="/" className="brand">
            Primerycomb
          </Link>
          <p className="muted tiny">Parent view · supplement, not replacement</p>
        </div>
        <nav className="nav">
          <Link href={`/session?id=${learner.id}`}>Back to session</Link>
        </nav>
      </header>

      <section className="panel parent-hero">
        <p className="eyebrow">Today with {learner.name}</p>
        <h1>What a devoted tutor would tell you</h1>
        <p className="lede">
          Not streaks. Not points. A clear picture of how {learner.name} is thinking —
          and what to try next at the kitchen table.
        </p>
      </section>

      <div className="home-grid">
        <article className="panel">
          <p className="eyebrow">What clicked</p>
          <List items={learner.whatClicked} empty="No breakthroughs logged yet." />
        </article>
        <article className="panel">
          <p className="eyebrow">What’s stuck</p>
          <List items={learner.whatStuck} empty="Nothing stuck — keep going." />
        </article>
        <article className="panel">
          <p className="eyebrow">Misconceptions spotted</p>
          <List
            items={learner.misconceptions}
            empty="None yet. Wrong answers will surface them."
          />
        </article>
        <article className="panel">
          <p className="eyebrow">How they learn best</p>
          <List
            items={learner.preferredExplanations}
            empty="Still discovering — usually after 1–2 sessions."
          />
        </article>
      </div>

      <section className="panel">
        <p className="eyebrow">Tutor notes</p>
        <p>{learner.notes}</p>
        <p className="muted tiny">
          Sessions: {learner.sessionCount} · Focus: {learner.skillFocus} · Affect:{" "}
          {learner.affect}
          {learner.lastProblem ? ` · Last problem: ${learner.lastProblem}` : ""}
        </p>
      </section>
    </main>
  );
}

function List({ items, empty }: { items: string[]; empty: string }) {
  if (!items.length) return <p className="muted">{empty}</p>;
  return (
    <ul>
      {items.map((i) => (
        <li key={i}>{i}</li>
      ))}
    </ul>
  );
}

export default function ParentPage() {
  return (
    <Suspense fallback={<main className="shell">Loading…</main>}>
      <ParentInner />
    </Suspense>
  );
}