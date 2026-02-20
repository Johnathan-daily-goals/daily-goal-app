# Daily Goal App — Frontend

React + TypeScript frontend for the daily goal tracker.

## Stack

- React 19 + Vite
- Tailwind CSS v4
- TypeScript

## Dev setup

```bash
npm install
npm run dev
```

Needs the Flask backend running on port 8000. The Vite dev server proxies `/auth`, `/projects`, and `/health` to it, so no CORS config is needed locally.

## Build

```bash
npm run build
```
