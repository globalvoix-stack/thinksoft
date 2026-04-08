# Thinksoft Landing Page

A React + Vite landing page for Thinksoft with Clerk authentication, a post-login dashboard, and a Neon PostgreSQL backend.

## Architecture

- **Framework**: React 19 + Vite 6
- **Styling**: Tailwind CSS v4 (via `@tailwindcss/vite` plugin), with `@import "tailwindcss"` syntax
- **Animations**: Framer Motion (`motion/react`)
- **Icons**: Lucide React
- **Language**: TypeScript
- **Auth**: Clerk (`@clerk/clerk-react`) — real authentication with Google, Apple, Microsoft, email/password
- **Database**: Neon PostgreSQL via `@neondatabase/serverless` + Drizzle ORM
- **Backend**: Express API server on port 3001, proxied through Vite at `/api`

## File Structure

All source files live at the project root (flat structure):
- `main.tsx` — React entry point, wraps app with `ClerkProvider` (shows setup prompt if key is missing)
- `App.tsx` — Landing page + routing
- `pages/Login.tsx` — Clerk `<SignIn>` component at `/login/*`, redirects to `/dashboard`
- `pages/SignUp.tsx` — Clerk `<SignUp>` component at `/signup/*`, redirects to `/dashboard`
- `pages/Dashboard.tsx` — Authenticated dashboard with collapsible sidebar and hero prompt area
- `pages/AllProjects.tsx` — All projects grid/list view with search/filter
- `pages/Starred.tsx`, `pages/CreatedByMe.tsx`, `pages/SharedWithMe.tsx` — Project filter views
- `pages/ProjectsLayout.tsx` — Shared sidebar layout used by Starred/CreatedByMe/SharedWithMe
- `server/index.ts` — Express API server (port 3001)
- `server/db.ts` — Neon/Drizzle database connection
- `server/schema.ts` — Drizzle ORM schema (projects, project_members tables)
- `server/migrate.ts` — One-time migration script to create tables
- `drizzle.config.ts` — Drizzle Kit config
- `index.css` — Global styles (Tailwind v4 + Google Fonts)
- `index.html` — HTML entry
- `vite.config.ts` — Vite config (port 5000, proxies /api → localhost:3001)
- `postcss.config.mjs` — PostCSS config (empty plugins, Tailwind handled by Vite plugin)
- `tsconfig.json` — TypeScript config
- `package.json` — Dependencies and scripts

## Routing

- `/` — Public landing page (shows Log in / Get started if not signed in, Dashboard if signed in)
- `/login/*` — Clerk sign-in (wildcard needed for Clerk's internal routing)
- `/signup/*` — Clerk sign-up (wildcard needed)
- `/dashboard` — Protected dashboard; if not signed in, Dashboard component redirects to `/login`

## Environment Variables

- `VITE_CLERK_PUBLISHABLE_KEY` — Clerk publishable key (required, from clerk.com). Without it, the app shows a setup prompt.
- `NEON_DATABASE_URL` — Neon PostgreSQL connection string (server-side only, never exposed to browser).

## Database

Tables created via `npm run migrate`:
- `projects` — user projects (id, clerk_user_id, title, description, image_url, is_starred, is_active, created_at, updated_at)
- `project_members` — shared project membership (id, project_id, clerk_user_id, role, joined_at)

API endpoints (all require `x-clerk-user-id` header):
- `GET /api/health` — DB connection check
- `GET /api/projects` — fetch owned + shared projects
- `POST /api/projects` — create a project
- `PATCH /api/projects/:id` — update a project
- `DELETE /api/projects/:id` — delete a project

## Assets

Static assets (images, videos) stored at root. Placeholder 1x1 pixel assets were created during Replit import setup for files originally missing from the repo:
- `background.png.png`, `auth.png`, `databases.png`, `storage.png`, `notifications.png`, `realtime.png`, `hosting.png`, `cta-bg.png`, `logo.png`
- `scene1.mp4.webm`, `scene2.mp4.webm`, `scene3.mp4.webm`

Replace these placeholder files with actual assets as needed.

## Development

```
npm run dev
```

Runs both the Express API server (port 3001) and the Vite dev server (port 5000) concurrently. Vite proxies all `/api` requests to Express. To run the API server alone: `npm run server`.

## Deployment

Configured as a static site:
- Build: `npm run build`
- Output: `dist/`
