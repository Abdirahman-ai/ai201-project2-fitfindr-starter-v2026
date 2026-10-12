# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6
> python app.py fields
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> The rest of this file is the project submission.

---

<!-- ====================== UNIT 3 — THE BUILD ====================== -->

## What This Does

FitFindr is an agent that helps a user search thrift listings and build an outfit around a selected item. The user can describe what they want, including an optional size and maximum price. The agent searches the available listings, chooses a matching item, suggests ways to style it using the user's wardrobe, and creates a short fit-card caption. If no listing matches, the agent stops early and tells the user what they could change in their search.

---

## Tool Inventory

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

The search uses the available listing information to match the user's description while also filtering by `size` and `max_price`.

**When nothing matches:**  
Returns an empty list `[]`.

---

### 2. `suggest_outfit(new_item, wardrobe)`

**What it does:**  
Uses the selected listing and the user's existing wardrobe to suggest an outfit that works with the new item.

**Inputs:**

- `new_item` (`dict`) — one listing returned by `search_listings`.
- `wardrobe` (`dict`) — the user's wardrobe dictionary, with an `items` key containing a list of wardrobe item dictionaries.

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

## Planning Loop

**Branch rule:**  
If `search_listings` returns an empty list, store a helpful message in the session telling the user what they could change, then stop before calling `suggest_outfit`. Otherwise, select the first matching listing, store it in the session, and continue to `suggest_outfit` and then `create_fit_card`.

**Where it lives:**  
`agent.py::run_agent`

**How the query is parsed:**  
The query is parsed with regular expressions and simple string cleanup. A regex extracts a maximum price from phrases such as `under $30` and a requested size from phrases such as `size M`. Those parts are then removed from the original query, and the remaining text is used as the item description.

**What moves through the session:**  
The parsed `description`, `size`, and `max_price` are stored in `session["parsed"]`. The results from `search_listings` are stored in `session["search_results"]`. If results exist, the first result is stored in `session["selected_item"]`.

That stored item and `session["wardrobe"]` are then used by `suggest_outfit`, whose result is stored in `session["outfit_suggestion"]`. Finally, `create_fit_card` uses the stored outfit suggestion and selected item, and its result is stored in `session["fit_card"]`.

If search returns no matches, a useful message is stored in `session["error"]` and the later tools are not called.

---

## Sample Run

### Full agent run

Command:

```bash
python app.py ask 'vintage graphic tee under $30'
```

Output:

```text
Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

Outfit:   Here are two cute and easy ways to style your new Y2K butterfly baby tee using pieces from your wardrobe:

Outfit 1: Casual Y2K Streetwear
- Bottoms: Baggy straight-leg jeans (dark wash)
- Shoes: Chunky white sneakers
- Accessories: Black crossbody bag
- Why it works: The fitted, graphic nature of the baby tee balances out the baggy, high-waisted denim for that ultimate 2000s off-duty look.

Outfit 2: Edgy Contrast
- Outerwear: Vintage black denim jacket
- Bottoms: Wide-leg khaki trousers
- Shoes: Black combat boots
- Accessories: Brown leather belt
- Why it works: Pairing the sweet, pastel cottagecore butterfly print with rugged black boots and a denim jacket creates a cool contrast between soft and edgy.

Fit card: Obsessed with this Y2K butterfly baby tee I just scored on Depop for only $18! The pastel pink and purple print is giving major sweet cottagecore energy, but I love styling it with baggy dark-wash jeans and chunky sneakers for that ultimate 2000s off-duty look. Such a cute and nostalgic piece to add to the rotation!

0 model calls this session, 2 served from cache
```

### Per-tool tests

#### `search_listings`

Command:

```bash
python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
```

Output:

```text
[
  {
    'id': 'lst_002',
    'title': 'Y2K Baby Tee — Butterfly Print',
    'size': 'S/M',
    'price': 18.0,
    'platform': 'depop',
    ...
  },
  {
    'id': 'lst_006',
    'title': 'Graphic Tee — 2003 Tour Bootleg Style',
    'size': 'L',
    'price': 24.0,
    'platform': 'depop',
    ...
  },
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

---

## How I Used AI

**Moment 1**

- **What I asked for:** I asked ChatGPT to review my `search_listings` tool specification and implementation before I wired it into the agent.
- **What came back:** It pointed out that `size` and `max_price` are optional inputs and that size matching needed to avoid simple substring checks such as matching `S` inside `US 9`.
- **What I changed:** I updated my README to show `size` and `max_price` as optional, and I implemented safer size matching by splitting values such as `S/M` into separate size parts instead of using a plain substring search.

**Moment 2**

- **What I asked for:** I asked ChatGPT to help me check the planning loop and session state in `agent.py`.
- **What came back:** It suggested parsing the query with regular expressions and simple string cleanup, then storing the parsed values, search results, selected item, outfit suggestion, and fit card in the session before each next tool call.
- **What I changed:** I implemented the query parser and made the later tools read their inputs back from the session. I also added the empty-search branch so the agent stores a useful error message and stops before calling `suggest_outfit`.

---

<!-- ======================= UNIT 4 — THE TEST ======================= -->

## Run Log — Before

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools and returns a fit card | 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 2. No-match query stops early and explains what to change | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 3. Selected item stays consistent through session state | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 4. Fit card mentions the selected item and a styling idea | 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 5. Search respects the requested maximum price | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |

**Real output from one try**, from `results/run_2026-10-11_2059_before.md`, produced by `run_eval.py` calling `agent.py::run_agent`:

```text
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

[1] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more

[2] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two ways to style your new Y2K butterfly baby tee using pieces you already own...

[3] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Just scored this precious Y2K butterfly baby tee for only $18 on Depop...
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools and returns a fit card | 4/5 | MET — 5/5 | All five runs completed all three tools and returned a fit card. |
| 2 | No-match query stops before `suggest_outfit` and explains what to change | 5/5 | MET — 5/5 | All five runs stopped after search and returned the expected guidance. |
| 3 | Selected item stays consistent through session state | 5/5 | MET — 5/5 | The same selected listing was passed through the later tool steps in all five runs. |
| 4 | Fit card mentions the selected item and a styling idea | 4/5 | MET — 5/5 | All five cards referenced the selected item and at least one outfit detail. |
| 5 | Search respects the requested maximum price | 5/5 | MET — 5/5 | Every run returned only results within the requested price limit. |

**Diagnoses**

None of my five criteria missed their targets. If I tightened one criterion, I would change Criterion 1 from 4 of 5 successful runs to 5 of 5. The before evaluation completed the full three-tool path and returned a fit card in all five runs, so the current 4-of-5 target may be more lenient than necessary.

---

## Loop Trace

**Happy path**

```text
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more

[2] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two ways to style your new Y2K butterfly baby tee using pieces you already own...

[3] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Just scored this precious Y2K butterfly baby tee for only $18 on Depop...
```

**Empty search**

```text
[1] search_listings
      in:  dict with keys: description, size, max_price
      out: [] (empty)
```

**On the MCP move:**  
I moved `search_listings` behind MCP. The agent now calls it through `mcp_client.call_tool(...)` instead of importing and calling the function directly. The returned value stayed the same: a list of listing dictionaries, so the rest of the planning loop did not need to change.

---

## The Improvement

**What I changed:**  
I improved the empty-search response so it includes the item description that failed to find a match. Previously, the response only said that no matching listing was found. Now the agent tells the user which description was searched and still suggests changing the budget, size, or description.

**Which failure it was meant to fix:**  
None of my five acceptance criteria failed in the Before evaluation. I chose to improve the empty-search branch because its response was useful but generic. The new message gives the user more context without changing the search or planning-loop behavior.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools and returns a fit card | 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 2. No-match query stops early and explains what to change | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 3. Selected item stays consistent through session state | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 4. Fit card mentions the selected item and a styling idea | 4/5 | MET | MET | MET | MET | MET | MET — 5/5 |
| 5. Search respects the requested maximum price | 5/5 | MET | MET | MET | MET | MET | MET — 5/5 |

**Did it help, and how do I know:**  
Yes. The overall criterion scores stayed the same at 5/5 across all five criteria, but the empty-search response became more useful. Before, it only said that no matching listing was found. After the change, it also tells the user which item description failed, for example `designer ballgown`, while preserving the same correct early-stop behavior.

The official After evaluation is stored in:

`results/run_2026-10-11_2145_after.md`

---

## What's Still Broken

The system still uses simple keyword matching for `search_listings`, so some
valid listings may be missed if the user's wording is very different from the
listing text.

The fit-card and outfit tools also depend on a language model, so their exact
wording can vary between runs. The acceptance criteria handle this by checking
whether the outputs stay grounded in the selected item and outfit rather than
requiring identical wording.

The project also starts a new MCP server connection for each tool call. This
works for the assignment and keeps the implementation simple, but it is less
efficient than keeping a long-lived MCP connection open.

---

## Submission Checklist — Unit 3

- [x] `criteria.md` has five numbered criteria, each with a target
- [x] Each criterion has a reason underneath it
- [x] All five Unit 3 sections above have real content
- [x] Tool Inventory includes all three tools, inputs with types, a specific return value, and the empty case
- [x] Planning Loop names the branch rule and `agent.py::run_agent`
- [x] Sample Run includes one full query plus the three per-tool tests as text
- [x] At least four new commits
- [x] Repository URL submitted

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**