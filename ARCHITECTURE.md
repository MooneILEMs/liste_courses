# Architecture

A reading note to understand what each file does, without needing prior web knowledge.

## The principle

There's no server. Nobody runs a program somewhere for you.

There's a page, copied to both phones on every open, and a data file in the repo that acts as the single source of truth. Both phones read and rewrite that file, each on their own. GitHub plays three distinct roles, which is what makes the setup a bit confusing at first:

| Role | What it is | Paid by |
|---|---|---|
| Host | GitHub Pages serves `docs/` | free (public repo) |
| Database | `data/liste.json` in the repo | free |
| Automation | GitHub Actions sends the email | free |

```
        Phone 1                                      Phone 2
        ┌──────────┐                                 ┌──────────┐
        │  the page│                                 │  the page│
        └────┬─────┘                                 └────┬─────┘
             │  write / read                 read / write │
             │        (GitHub API + token)                 │
             └────────────────┐         ┌──────────────────┘
                              ▼         ▼
                    ┌──────────────────────────┐
                    │   data/liste.json        │   ← the GitHub repo
                    └────────────┬─────────────┘
                                 │  every write = 1 commit
                                 ▼
                    ┌──────────────────────────┐
                    │   GitHub Actions         │
                    │   .github/workflows      │
                    └────────────┬─────────────┘
                                 │  Gmail SMTP
                                 ▼
                          email to the other person
```

The page itself arrives through a separate, tokenless path: the phone downloads it from `docs/` on first load, then keeps it cached. It contains no data.

## The lifecycle of a change

It's a real sequence, in this order:

1. You type "milk" and confirm. The item is added to a list held in the phone's memory.
2. The screen redraws immediately. Nothing has gone over the network yet — that's why it never lags.
3. The list is copied into the browser's local storage. If you close everything right now, nothing is lost.
4. A 2.5s countdown starts. Every new keystroke resets it, which avoids one commit per item.
5. The countdown hits zero: the phone sends the whole file to the GitHub API, with the commit message `liste: maj par Jean`.
6. GitHub writes the file, creates the commit, and triggers the workflow.
7. The workflow reads the first name from the message, figures out who to email, extracts the items not yet checked off, and sends the email.
8. The other phone, meanwhile, re-requests the file every 20s while the app is open, and merges whatever it gets back.

Step 5 deserves a note. The GitHub API requires the `sha` of the version it believes it's modifying. If the other person wrote in the meantime, that `sha` is stale and GitHub refuses (409 error). The app then re-reads the current version, merges item by item keeping the most recent of the two timestamps, and retries. That's what stops one write from overwriting the other.

## What's in each file

| File | Role | Modified by |
|---|---|---|
| `docs/index.html` | the whole app: structure, appearance, behavior | you, by hand |
| `docs/manifest.json` | enables adding it to the home screen | never |
| `docs/icon.png` | the app icon (PNG, not SVG — Android launchers handle SVG-only icons poorly) | never |
| `docs/.nojekyll` | tells Pages to publish the files as-is | never |
| `data/liste.json` | the list | the app, automatically |
| `.github/workflows/notif.yml` | the email recipe | you, if you change the SMTP setup |

The token isn't anywhere in this list, and that's deliberate. It lives in each phone's browser.

## What's inside index.html

A web file holds three things of a different nature. Here they're all stacked in the same file, since there's no need for more.

**The structure** — the `<h1>`, `<ul>`, `<input>` tags. This describes *what* is on screen, without saying what it looks like. It's the tree, the equivalent of a widget hierarchy. It's short here: a title, a status line, an empty list, an input field, a settings window.

**The style** — the `<style>` block. This describes *how* it's presented: colors, sizes, spacing. Elements are selected by name or class and given properties. The project's colors and dimensions are grouped at the top under `:root` — that's where to look to change the look:

```
--papier    #EFF1EC   the background
--encre     #1B2A22   the text
--stylo     #1D3FBE   the strikethrough line, the buttons
--marge     #D4453C   the vertical red margin rule
--reglure   #C3D0E8   the horizontal lines
--ligne     34px      the height of one notebook line
```

**The behavior** — the `<script>` block. This is JavaScript, and the only place with any logic. The functions are named in French:

```
etatDoc          the list held in memory
rendre()         redraws the screen from etatDoc
modifier()       applies a change, saves locally, schedules the send
tirer()          reads the file from GitHub and merges
pousser()        writes the file to GitHub
fusionner()      arbitrates between two versions, item by item
synchroniser()   decides whether to pull or push
```

Nothing else. No library, no build step, no `npm install`. The file you open is exactly the one that runs, which makes debugging direct.

## The layout

A single column, centered, never wider than 560px. On a phone it fills the screen; on a computer it stays in the middle.

```
┌─────────────────────────────────────────┐
│ │                                       │  ← vertical red margin rule
│ │  La liste                             │     title
│ │  À jour                               │     status line (tap = settings)
│ │ ─────────────────────────────────     │
│ │  lait                                 │  ← lines are aligned
│ │ ─────────────────────────────────     │     on the notebook rule
│ │  farine                    ELSA       │  ← first name shown if the other added it
│ │ ─────────────────────────────────     │
│ │  c̶a̶f̶é̶                          ×      │  ← crossed out, sunk to the bottom
│ │ ─────────────────────────────────     │
│ │  Retirer ce qui est pris              │
│ │ ─────────────────────────────────     │
│ │                                       │
│ │            (empty space)              │
│ │                                       │
├─────────────────────────────────────────┤
│  [ Ajouter…            ]  [ Ajouter ]   │  ← fixed at the bottom, within thumb's reach
└─────────────────────────────────────────┘
```

Three decisions worth knowing, because they explain the rest of the style:

The background is an image repeated every 34px, generated in CSS, not a file. The text's line height is exactly those 34px, so every item lands right on a line. If you change the text size without changing `--ligne`, the alignment breaks — the two values move together.

The input field is fixed at the bottom of the screen. On a phone held in one hand in a store, it's the only zone reachable by thumb without contorting. The title, meanwhile, has no functional importance, and so occupies the least accessible zone.

Checked-off items automatically sink to the bottom and get struck through with a blue line drawn in 0.22s. The strikethrough isn't a special character but a 2px blue rectangle whose width animates from 0 to 100%. That's what gives the impression of a pen stroke running across.
