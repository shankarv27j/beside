import type { LearnerModel, PedagogyMove, AffectState } from "@/lib/types";

const moveLabels: Record<PedagogyMove, string> = {
  diagnose: "Diagnose",
  hint: "Hint",
  scaffold: "Scaffold",
  reframe: "Reframe",
  celebrate: "Celebrate",
  retreat: "Retreat",
  check: "Check",
};

export function LearnerModelPanel({
  learner,
  lastMove,
  lastAffect,
}: {
  learner: LearnerModel;
  lastMove?: PedagogyMove;
  lastAffect?: AffectState;
}) {
  return (
    <aside className="panel model-panel">
      <p className="eyebrow">Learner model</p>
      <h2>
        {learner.name}, {learner.age}
      </h2>
      <p className="muted">Loves {learner.interest}</p>

      <dl className="stats">
        <div>
          <dt>Sessions</dt>
          <dd>{learner.sessionCount}</dd>
        </div>
        <div>
          <dt>Affect</dt>
          <dd>{lastAffect || learner.affect}</dd>
        </div>
        <div>
          <dt>Last move</dt>
          <dd>{lastMove ? moveLabels[lastMove] : "—"}</dd>
        </div>
        <div>
          <dt>Focus</dt>
          <dd>{learner.skillFocus}</dd>
        </div>
      </dl>

      <Section title="What clicked" items={learner.whatClicked} empty="Not yet" />
      <Section title="What's stuck" items={learner.whatStuck} empty="Nothing logged" />
      <Section
        title="Misconceptions"
        items={learner.misconceptions}
        empty="None yet"
      />
      <Section
        title="Preferred explanations"
        items={learner.preferredExplanations}
        empty="Still learning"
      />

      {learner.notes ? (
        <div className="note">
          <p className="eyebrow">Tutor notes</p>
          <p>{learner.notes}</p>
        </div>
      ) : null}
    </aside>
  );
}

function Section({
  title,
  items,
  empty,
}: {
  title: string;
  items: string[];
  empty: string;
}) {
  return (
    <div className="section">
      <p className="eyebrow">{title}</p>
      {items.length === 0 ? (
        <p className="muted">{empty}</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}