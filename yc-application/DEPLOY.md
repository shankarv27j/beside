# Get a public demo URL (required for YC)

Vercel deploy needs your login once (CLI token isn’t available in this environment).

```bash
cd web
npx vercel login
npx vercel --yes
npx vercel --prod --yes
```

Paste the production URL into:

1. YC application “Company URL” / demo link fields  
2. [`ANSWERS.md`](ANSWERS.md) progress section  

**Local fallback for recording today:**

```bash
cd web
npm run dev
```

Open http://localhost:3000 → create learner → **Demo Play** → record with Loom.
