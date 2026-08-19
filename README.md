# La liste

A shared shopping list for two, built as a static page on GitHub Pages that emails the other person whenever the list changes.

## How it works

The browser reads and writes `data/liste.json` through the GitHub API, using a token entered once per device and kept locally. Every write creates a commit; the workflow reads the author from the commit message and emails the other person.

The published site is limited to `docs/`. The data lives in `data/`, outside the published folder: the app reaches it through the API, never through the site's URL. A private repo therefore makes the list genuinely inaccessible, even though the page itself stays reachable to anyone with the address.

```
docs/          published by Pages — the page, nothing sensitive
data/          the list — never served by the site
.github/       the workflow that sends the email
```

Changes are batched: the send goes out 2.5s after the last keystroke, not on every item. Offline, everything stays usable and syncs back up on reconnection.

## Setup

**1. The repo**

Create the repo, push these files, then Settings → Pages → Source: `Deploy from a branch`, branch `main`, folder **`/docs`**.

Make the repo private if you want the list to be private too: `data/liste.json` is then visible neither on github.com nor on the site. Pages from a private repo requires a Pro account — free via the GitHub Student Developer Pack. With a public repo, the file stays readable on github.com by anyone.

Either way, the published page is reachable by anyone who knows the URL. That's not a problem: without a token, it's empty.

**2. The names**

In `docs/index.html`, replace the line `const NOMS = ["Jean", "Ma conjointe"];` with your two first names. They must match the secrets below exactly.

**3. The token, on each phone**

Settings → Developer settings → Personal access tokens → Fine-grained tokens.

- Repository access: this repo only
- Permissions → Repository → Contents: **Read and write**
- Expiration: 1 year max, renew as needed

Open the site, the connection window appears: repo (`username/liste-courses`), who you are, token. To reopen it later, tap the status line under the title.

The token stays in the device's browser. Its scope is limited to this repo: worst case, someone edits the shopping list.

**4. The email**

The workflow goes through Gmail's SMTP. It needs 2-step verification enabled, then an app password: myaccount.google.com → Security → App passwords.

Settings → Secrets and variables → Actions, add:

| Secret | Value |
|---|---|
| `SMTP_USER` | the Gmail address that sends |
| `SMTP_PASS` | the app password (16 characters) |
| `NOM_A` | the first name, identical to `NOMS[0]` |
| `MAIL_A` | their address |
| `MAIL_B` | the other person's address |

**5. On the phone**

Add the page to the home screen: it opens full-screen, without a browser bar.

## Usage

Type then Enter to add. Tap a line to cross it out. The × removes the item, "Retirer ce qui est pris" clears the crossed-out lines all at once.

## Limits

- About 2 to 3 seconds between a change and its appearance on the other device; the screen refreshes every 20s while open.
- Simultaneous edits: the most recent version of each item wins, item by item. Nothing is lost, but two edits to the same item within the same second can overwrite one another.
- Removed items are kept for 7 days in the file before being purged, giving both devices time to see the deletion.
- One commit per change: the repo's history grows fast. Harmless, but visible.
