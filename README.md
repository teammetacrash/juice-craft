# JUICE CRAFT

An admin-only shop workspace for ice cream, juices and prepared drinks.

## Current application

- **Website:** React + TypeScript, built with Vite in `web/`.
- **Hosting:** GitHub Pages, published by `.github/workflows/pages.yml`.
- **Backend:** Supabase Edge Function `juicecraft-shop` and private PostgreSQL schema `juicecraft`.
- **Brand:** #8B09A2 and white, with locally hosted Inter typography.

The original Django files are retained in this repository. The current GitHub Pages application uses the Supabase backend directly.

## Features

Admin login; daily totals; revenue, known profit and bill graphs for 7 days, 30 days, 90 days or all time; packaged stock; editable categories and brands; prepared items; deliveries; wastage; expenses; date-filtered sales; CSV exports; downloadable PDF bills. On phones, the app has a bottom navigation bar and product cards with a large Edit item button. Back and Dashboard controls are always visible.

Prepared items do not ask for profit. Known profit includes packaged margins minus recorded losses and expenses; ingredient costs are not tracked. All-time graphs use monthly totals when the history exceeds 90 days. Old bills retain the item names and prices recorded at the time of sale.

## Development

Use Node 24. From `web/`, run `npm ci`, then `npm run dev`. Run `npm run build` to check types and build. `GITHUB_PAGES=true npm run build` builds with the repository base path.

Development-only `/__design` and `/__responsive` routes use synthetic in-memory fixtures for desktop and 390px phone checks. They never access real shop records and are removed by the production build.

## Publishing

In repository Settings → Pages, set **Source** to **GitHub Actions** once. Pushes to `main` affecting the frontend or workflow then publish automatically. The workflow uses the official GitHub Pages actions. No paid hosting configuration is required by this repository.

The Supabase function source and schema are in `web/supabase/`. The function uses its built-in server database credential; no database password, service-role key or admin password belongs in the browser or repository. Deploy with JWT verification disabled only because this function implements its own hashed admin sessions and verifies every protected request. Anonymous REST access to the private shop schema is revoked. CORS permits only `https://teammetacrash.github.io`.

Sessions expire after two hours of inactivity, are hashed in the database, and are stored only for the browser tab's session. Sign-out revokes the server session. Database transactions and a transaction-level shop lock prevent overselling, duplicate retries and conflicting bill numbers.

PDFs are created on demand and saved on the customer's device; PDFs do not consume Supabase file storage. Database rows still grow over time. Free provider limits can change, so export reports and monitor usage.
