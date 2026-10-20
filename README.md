# EE471 Week 4: Eray Erdogan

In-class exercise for Week 4 of EE471 Modern Software Development Practices and Technologies.

## Repository Structure

| Path | Content |
|---|---|
| `Section 1/` | Calculator: Figma design, web page and Flask backend |
| `Section 2/` | Library app |
| `EE471_MP1_Calculator/` | Mini Project 1, included as a Git submodule |
| `EE471-week3/` | Week 3 library classes, included as a Git submodule |

## Submodules

Earlier projects are added to this repository as **Git submodules** instead of being copied:

| Submodule | Repository | Used in |
|---|---|---|
| `EE471_MP1_Calculator/` | [Mini Project 1](https://github.com/erdoganeray/EE471_MP1_Calculator) | Section 1 imports the `Calculator` class from its `custom_classes.py` and extends it; the file is not copied or modified. |
| `EE471-week3/` | [Week 3](https://github.com/erdoganeray/EE471-week3) | Starting point of Section 2: the library classes in `custom_classes.py` and `main.py`. |

Clone together with the submodules:

```bash
git clone --recurse-submodules https://github.com/erdoganeray/EE471-week4.git
```

If the repository was already cloned without them:

```bash
git submodule update --init
```

## Section 1: Calculator

### Part 1: Figma Design

The calculator was designed in Figma using Auto Layout.

- **Figma (view-only):** [Calculator design](https://www.figma.com/design/hRnuiYD8ZNH0RvK3OD1u9U/Untitled?node-id=1-49&t=yzAbhp5yi4yyd6s0-1)

![Calculator design](Section%201/design/calculator.png)

### Part 2: Web Page and Flask Backend

The web page was generated from the Figma design with an AI coding tool. All calculations run on a Flask server that uses the Mini Project 1 `Calculator` class. Prompts are in [PROMPTS.md](Section%201/PROMPTS.md).

| File | Purpose |
|---|---|
| `static/index.html`, `style.css`, `script.js` | Calculator page. `script.js` sends every calculation to the API. |
| `web_calculator.py` | `WebCalculator` extends the Mini Project 1 `Calculator`: input checks, a division by zero error and a `calculate(a, operator, b)` method. |
| `app.py` | Flask server: serves the page and `POST /api/calculate`. |
| `requirements.txt` | Python dependencies (`flask`). |

#### Run

```bash
cd "Section 1"
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000.

#### API: `POST /api/calculate`

Request body (`operator` is one of `+`, `-`, `*`, `/`):

```json
{"a": 7, "operator": "+", "b": 8}
```

| Case | Status | Response |
|---|---|---|
| Success | 200 | `{"result": 15}` |
| Division by zero | 400 | `{"error": "Cannot divide by zero"}` |
| `a` or `b` missing, not a number, `NaN` or `Infinity` | 400 | `{"error": "a and b must be numbers"}` |
| Unknown operator | 400 | `{"error": "operator must be one of + - * /"}` |
| Result too large for a number (e.g. `1e308 * 10`) | 400 | `{"error": "Result is too large"}` |
| Body is not a JSON object | 400 | `{"error": "Request body must be a JSON object"}` |

## Section 2: Library App

### Part 1: Figma Design (Bonus)

The single-page library app was designed in Figma with an AI coding tool through the Figma MCP server, using Auto Layout throughout. It contains:

- **Item Card** component with two variants, `Status=Available` and `Status=Checked out`, showing title, author, type, page count or duration and an availability badge, with Checkout/Return, edit and delete actions.
- **Main** screen with the "Available only" toggle, the All / Books / DVDs filter, an error message area and the item list.
- **Empty State** screen for a library with no items.
- **Add/Edit form**: the length field switches between page count (Book) and duration in minutes (DVD).

- **Figma (view-only):** [Library app design](https://www.figma.com/design/CZhIb4XToB6VuuPTPXXuTc/EE471-Week4-Library-App?node-id=0-1&t=lWF3u6F5ut9POitO-1)

![Library app design](Section%202/design/library.png)

### Part 2: CRUD Methods

`custom_classes.py` and `main.py` in `Section 2/` are copied from the Week 3 submodule and extended with unique item ids, `to_dict()`, the `ItemNotFoundError` and `ItemStateError` exceptions, and `get_item()`, `list_items()`, `update_item()` and `remove_item()` on `LibraryCollection`. Running `python main.py` calls every method and catches each exception. Prompts are in [PROMPTS.md](Section%202/PROMPTS.md).

### Part 3: Flask REST API

`app.py` exposes one `LibraryCollection` through a REST API. The routes only translate HTTP to method calls; all rules live in `custom_classes.py`. Every response is JSON, and errors are `{"error": "<message>"}`.

The server starts with four items: Dune (1, book), Interstellar (2, DVD), Arrival (3, DVD, checked out) and The Hobbit (4, book).

#### Run

```bash
cd "Section 2"
pip install -r requirements.txt
python app.py
```

The API runs at http://127.0.0.1:5000.

#### Endpoints

| Endpoint | Purpose | Success | Errors |
|---|---|---|---|
| `POST /api/items` | Create a Book or DVD | 201 + the new item | 400 |
| `GET /api/items` | List items; supports `?available=true` and `?type=book` | 200 | 400 bad filter |
| `GET /api/items/<id>` | Get one item | 200 | 404 |
| `PUT /api/items/<id>` | Replace all editable fields | 200 | 400, 404 |
| `PATCH /api/items/<id>` | Change some editable fields | 200 | 400, 404 |
| `DELETE /api/items/<id>` | Remove an item | 204 | 404, 409 if checked out |
| `POST /api/items/<id>/checkout` | Check an item out | 200 | 404, 409 already out |
| `POST /api/items/<id>/return` | Return an item | 200 | 404, 409 not checked out |

Request body for `POST /api/items`:

```json
{"type": "dvd", "title": "Arrival", "author": "Denis Villeneuve", "duration": 116}
```

A book uses `"type": "book"` and `page_count` instead of `duration`. `PUT` needs every editable field (`title`, `author`, and `page_count` or `duration`); `PATCH` takes any of them.

### Part 4: Web Page

The web page in `Section 2/static/` (`index.html`, `style.css`, `script.js`) was generated from the Figma design with an AI coding tool and is served by the same Flask server: run `python app.py` and open http://127.0.0.1:5000. Every action goes through the API above, and the API's error messages are shown in the error area (for example, deleting the checked-out Arrival shows the 409 message). The prompts and the bugs fixed after reviewing the generated code are in [PROMPTS.md](Section%202/PROMPTS.md).
