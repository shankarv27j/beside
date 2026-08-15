"use client";

import Link from "next/link";
import { useEffect, useState, type FormEvent } from "react";
import {
  createLearner,
  deleteLearner,
  listLearners,
  upsertLearner,
} from "@/lib/storage";
import type { LearnerModel } from "@/lib/types";

export default function HomePage() {
  const [learners, setLearners] = useState<LearnerModel[]>([]);
  const [name, setName] = useState("Asha");
  const [age, setAge] = useState(11);
  const [interest, setInterest] = useState("cricket");

  useEffect(() => {
    setLearners(listLearners());
  }, []);

  function refresh() {
    setLearners(listLearners());
  }

  function onCreate(e: FormEvent) {
    e.preventDefault();
    const learner = createLearner({ name, age, interest });
    upsertLearner(learner);
    refresh();
    window.location.href = `/session?id=${learner.id}`;
  }

  return (
    <main className="shell">
      <header className="hero">
        <p className="eyebrow">YC Primer wedge · Mentoring Loop</p>
        <h1 className="brand-hero">Primerycomb</h1>
        <p className="lede">
          An AI private tutor that learns each child the way a devoted mentor does —
          diagnose, scaffold, reframe, remember. Starting with reading + arithmetic
          through stories from their world.
        </p>
      </header>

      <div className="home-grid">
        <form className="panel" onSubmit={onCreate}>
          <p className="eyebrow">Start a child</p>
          <h2>New learner profile</h2>
          <label>
            Name
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={40}
            />
          </label>
          <label>
            Age
            <input
              type="number"
              min={8}
              max={14}
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              required
            />
          </label>
          <label>
            Interest (stories are built from this)
            <input
              value={interest}
              onChange={(e) => setInterest(e.target.value)}
              placeholder="cricket, cats, space…"
              required
            />
          </label>
          <button type="submit" className="primary">
            Begin mentoring session
          </button>
          <p className="muted tiny">
            Works offline without an API key. Add OPENAI_API_KEY in{" "}
            <code>web/.env.local</code> for live model turns.
          </p>
        </form>

        <section className="panel">
          <p className="eyebrow">Saved learners</p>
          <h2>Continue</h2>
          {learners.length === 0 ? (
            <p className="muted">No learners yet — create one to see the loop.</p>
          ) : (
            <ul className="learner-list">
              {learners.map((l) => (
                <li key={l.id}>
                  <div>
                    <strong>
                      {l.name}, {l.age}
                    </strong>
                    <span className="muted">
                      {" "}
                      · {l.interest} · {l.sessionCount} sessions
                    </span>
                  </div>
                  <div className="row-actions">
                    <Link href={`/session?id=${l.id}`}>Session</Link>
                    <Link href={`/session?id=${l.id}&demo=1`}>Demo Play</Link>
                    <Link href={`/parent?id=${l.id}`}>Parent</Link>
                    <button
                      type="button"
                      className="linkish"
                      onClick={() => {
                        deleteLearner(l.id);
                        refresh();
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="panel loop-explain">
        <p className="eyebrow">What you’re showcasing</p>
        <h2>The mentoring loop</h2>
        <ol className="loop">
          <li>Diagnose state</li>
          <li>Choose a pedagogy move</li>
          <li>Deliver in their language</li>
          <li>Observe reaction</li>
          <li>Update learner model</li>
        </ol>
      </section>
    </main>
  );
}