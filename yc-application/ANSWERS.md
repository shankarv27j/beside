# YC Fall 2026 — Beside (full answers)

Copy-paste into the form. Replace only `[BRACKETS]`.

**Deadline:** July 27, 2026 ~8:00pm PT  
**Thesis:** Beside = a 1:1 AI tutor that is a replica of how I mentor — sits beside the child, starts small, learns them, progresses. Starts with reading, writing, arithmetic. Optional short game at end of session. Path to Primer.

---

## Founders

### Who writes code, or does other technical work on your product? Was any of it done by a non-founder? Please explain.

I write the code and do all technical work. Solo founder. No non-founders involved.

### Are you looking for a cofounder?

No.

### Founder video

Record ~60s, you talking only (no product demo). Upload under 100 MB.

**Bullets to say:**
- I’m [Name]. Building Beside — a 1:1 AI tutor that mentors like I do.
- I’ve mentored 100+ US kids remotely from India for ~3 years. I know how to start small, read a child, and level them up.
- Reading, writing, arithmetic first; short sessions; I’m encoding my mentoring craft into the AI.
- Applying YC Fall 2026 / Primer RFS.

---

## Company

### Company name*

Beside

### Describe what your company does in 50 characters or less.*

1:1 AI tutor that grows with each child

*(38 characters)*

### Company URL, if any

*(leave blank)*

### If you have a demo, attach it below.

*(leave blank — no demo)*

### Please provide a link to the product, if any.

*(leave blank)*

### Login credentials

*(leave blank)*

### What is your company going to make? Please describe your product and what it does or will do.

Beside is a 1:1 AI tutor for kids ages 8–14 that is a replica of how I mentor: it sits beside the child, notices how they’re stuck, starts small, explains until it clicks, and remembers what works for them across sessions. We start with reading, writing, and arithmetic.

Parents buy it as a home supplement, not a school replacement. Sessions are short and focused; optionally a small game at the end tied to what they learned. Long term, that same mentor grows with the child — the Primer path.

### Where do you live now, and where would the company be based after YC?

[Your city], India / San Francisco, USA

### Explain your decision regarding location.

I live in India and work remotely for YoungWonks as a 1:1 mentor for US kids — live video across US time zones. Parents have given strong feedback on how my mentoring helped their kids in the US. Early customers will likely be US parents seeking remote 1:1 help, since that’s who I already mentor today. I’d be in San Francisco for the YC batch; afterward I’d keep building while operating from India, the same remote setup I use today.

---

## Progress

### How far along are you?

No shipped product yet. Domain-wise I’m far along: ~3 years mentoring US kids 1:1 at YoungWonks (remote from India), 100+ students, 10+ parent emails on how mentoring helped their kids. Building Beside to encode that tutoring craft into an AI replica of how I mentor — starting with reading, writing, and arithmetic.

### How long have each of you been working on this? How much of that has been full-time? Please explain.

Solo founder. Underlying work — 1:1 mentoring of US kids — for ~3 years at YoungWonks (ongoing work, not a hobby). Building the Beside product since July 2026, full-time. Three years are domain expertise; the software is new.

### What tech stack are you using, or planning to use, to build this product? Include AI models and AI coding tools you use.

Python backend: FastAPI, PostgreSQL (Supabase or Neon), SQLModel, deployed on Railway/Render/Fly.io.

Tutor brain: OpenAI Python SDK (gpt-4o / gpt-4o-mini) with structured JSON turns (reply, pedagogy move, learner updates), plus a library of my real mentoring examples so the AI replicates how I teach.

Auth: Supabase Auth or Clerk (parent accounts).

Voice: OpenAI Whisper (speech-to-text) + OpenAI TTS (tutor speech).

Web UI: FastAPI + Jinja/HTMX classroom front end (React later if needed).

Curriculum: skill graphs for reading, writing, arithmetic in Postgres; optional end-of-session practice games.

AI coding tools: Cursor.

### Are people using your product?

No

### Do you have revenue?

No

### If you are applying with the same idea as a previous batch… / pivot?

N/A — first application.

### If you have already participated in an incubator / accelerator…

None.

---

## Idea

### Why did you pick this idea to work on? Do you have domain expertise in this area? How do you know people need what you’re making?

I’ve mentored US kids 1:1 for ~3 years at YoungWonks, remotely from India — 100+ students. What I actually do is notice how a child is stuck, start where they are, and level them up until it clicks. Parents have emailed me (10+) about how that mentoring helped their kids. US parents already pay for scarce devoted 1:1 tutors — the bottleneck is supply and consistency, not demand.

I picked this because I want an AI that is a replica of how I mentor — so every child can have that kind of tutor beside them. Beside starts with reading, writing, and arithmetic; the long game is a mentor that grows with the child. I already had this idea; YC’s Primer RFS matched it.

### Who are your competitors? What do you understand about your business that they don’t?

Closest products: Khanmigo, Synthesis Tutor, and generic GPT tutors. Closest alternative: live remote tutors (like what I do at YoungWonks).

What they miss: Khanmigo/Synthesis optimize adaptive content; ChatGPT has no real long-term model of a child; human tutors don’t scale. Nobody is building a 1:1 AI that is a replica of a specific mentor’s craft: how I diagnose stuckness, when I retreat, how I rebuild trust, what I remember across weeks. Beside is that: me at scale, starting with reading, writing, and arithmetic.

### How do or will you make money? How much could you make?

Parent-paid monthly subscription, around $99/month per child, for frequent 1:1 AI sessions (about 30 minutes every other day). Later: family plans.

Estimate: 1,000 families × $99/month ≈ $1.2M ARR. 10,000 families × $99/month ≈ $11.9M ARR. Near term: charge early US parents once kids return for repeat sessions.

### If you had any other ideas you considered applying with, please list them.

A game-based learning product with a 1:1 AI mentor inside: kids play fun games that train problem-solving; the mentor starts small, learns the child, and unlocks the next challenge. About 30 minutes every other day. Same mentoring craft as Beside, different surface (games instead of reading/writing/arithmetic first).

---

## Equity

### Have you formed ANY legal entity yet?

No

### Have you taken any investment yet?

No

### Are you currently fundraising?

No

---

## Curious

### What convinced you to apply to Y Combinator? Did someone encourage you to apply? Have you been to any YC events?

I already wanted to build an AI that mentors like I do. Then I saw YC’s Fall 2026 Primer RFS, and it matched that idea, so I applied. Nobody specifically encouraged me. I have not been to a YC event.

### How did you hear about Y Combinator?

I’ve always wanted to build something, and in my research last year everything pointed to Y Combinator as the go-to for founders. That’s how I landed on the YC site. This year I came back for the Primer RFS and applied.

### What batch do you want to apply for?

Fall 2026

---

## Before submit

- [ ] Company name: Beside  
- [ ] Founder video uploaded  
- [ ] YC profile complete → refresh apply page  
- [ ] `[Your city]` and `[Name]` filled  
- [ ] Demo / URL left blank  
- [ ] How you heard about YC filled  
