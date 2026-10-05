# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### 1. `search_listings(description, size, max_price)`

**What it does:**  
Searches the listings data for items that match the user's description, requested size, and maximum price.

**Inputs:**
- `description` (`str`) — words describing the item the user wants.
- `size` (`str | None`) — requested size, or `None` if the user did not specify one.
- `max_price` (`float | None`) — maximum price, or `None` if the user did not specify a budget.

**Returns:**  
A list of matching listing dictionaries. Each listing can contain:

- `id` (`str`)
- `title` (`str`)
- `description` (`str`)
- `category` (`str`)
- `style_tags` (`list`)
- `size` (`str`)
- `condition` (`str`)
- `price` (`float`)
- `colors` (`list`)
- `brand` (`str` or `None`)
- `platform` (`str`)

The search should use the available listing information to match the user's description, while also filtering by `size` and `max_price`.

**When nothing matches:**  
Returns an empty list `[]`.

---

### 2. `suggest_outfit(new_item, wardrobe)`

**What it does:**  
Uses the selected listing and the user's existing wardrobe to suggest an outfit that works with the new item.

**Inputs:**
- `new_item` (`dict`) — one listing returned by `search_listings`.
- `wardrobe` (`list[dict]`) — the user's wardrobe items.

Each wardrobe item can contain:

- `id` (`str`)
- `name` (`str`)
- `category` (`str`)
- `colors` (`list`)
- `style_tags` (`list`)
- `notes` (`str`)

**Returns:**  
A string containing an outfit suggestion that combines the new item with useful pieces from the wardrobe.

**When the wardrobe is empty:**  
Returns general styling advice for the new item instead of failing.

---

### 3. `create_fit_card(outfit, new_item)`

**What it does:**  
Creates a short caption someone could realistically post for the outfit.

**Inputs:**
- `outfit` (`str`) — the outfit suggestion returned by `suggest_outfit`.
- `new_item` (`dict`) — the selected listing from `search_listings`.

**Returns:**  
A short fit-card caption as a string describing or presenting the outfit.

**When it cannot create a usable fit card:**  
Returns a short explanatory message rather than crashing.

---

## Planning Loop Branch Rule

If `search_listings` returns an empty list, store a message in the session telling the user that no matching listing was found and suggesting what they could change, such as increasing the budget, changing the size, or using a broader description. Then stop before calling `suggest_outfit`.

Otherwise, store the selected listing in the session as `selected_item`. Read `selected_item` back from the session and use it when calling `suggest_outfit`. Store the resulting outfit in the session, then read both the stored outfit and selected item from the session when calling `create_fit_card`.

---
## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:**  
If `search_listings` returns an empty list, store a helpful message in the session telling the user what they could change, then stop before calling `suggest_outfit`. Otherwise, select the first matching listing, store it in the session, and continue to `suggest_outfit` and then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:**  
The query will be parsed with regular expressions and simple string cleanup. A regex will extract a maximum price from phrases such as `under $30` and a requested size from phrases such as `size M`. Those parts will then be removed from the original query, and the remaining text will be used as the item description.

**What moves through the session:**  
The parsed `description`, `size`, and `max_price` are stored in `session["parsed"]`. The results from `search_listings` are stored in `session["search_results"]`. If results exist, the first result is stored in `session["selected_item"]`. That stored item and `session["wardrobe"]` are then used by `suggest_outfit`, whose result is stored in `session["outfit_suggestion"]`. Finally, `create_fit_card` uses the stored outfit suggestion and selected item, and its result is stored in `session["fit_card"]`. If search returns no matches, a useful message is stored in `session["error"]` and the later tools are not called.

### Per-tool tests

#### `search_listings`

Command:

```bash
python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
```

Output:

```text
[
  {'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'size': 'S/M', 'price': 18.0, 'platform': 'depop', ...},
  {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'size': 'L', 'price': 24.0, 'platform': 'depop', ...},
  ...
]
```

The search returned matching listings ranked by keyword overlap, and all returned items were at or below the $30 maximum price.

#### `suggest_outfit`

Command:

```bash
python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
```

Output:

```text
Here are two easy, everyday outfits using your new vintage Levi's 501s and pieces you already own:

Outfit 1: Effortless Casual
- White ribbed tank top
- Vintage black denim jacket
- Chunky white sneakers
- Black crossbody bag

Outfit 2: Cozy & Classic
- Oversized grey crewneck sweatshirt
- Brown leather belt
- Black crossbody bag
- Black combat boots
```

The tool used specific pieces from the provided wardrobe.

#### `create_fit_card`

Command:

```bash
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
```

Output:

```text
Nothing beats a broken-in pair of vintage Levi's 501s for nailing that effortless streetwear vibe. I’m obsessed with this medium wash pair—just style them with your favorite crisp white sneakers for the ultimate casual look. Grab them on Depop right now for only $38.00 before I change my mind and keep them!
```

The fit card included the selected item, price, platform, and styling idea.

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
