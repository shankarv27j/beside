# Primerycomb — Mentoring Loop Demo

YC Primer RFS wedge: adaptive 1:1 tutoring for young children (reading + arithmetic via word problems), with a persistent learner model.

## Quick start

```bash
cd web
cp .env.example .env.local   # optional: add OPENAI_API_KEY
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

- **Begin mentoring session** — create a child, chat as the child  
- **Demo Play** — scripted child turns for a YC product clip (`/session?id=...&demo=1`)  
- **Parent view** — what clicked / what’s stuck  

Works **without** an API key (offline tutor loop). With `OPENAI_API_KEY`, turns use the live model.

## Deploy (public URL for YC)

```bash
cd web
npx vercel --yes
```

Paste the URL into `yc-application/ANSWERS.md` and the YC form.

## What to show partners

Wrong answer → diagnose/scaffold (no shame) → “I don’t know” → retreat → correct answer → celebrate → learner model updates → Parent view.
