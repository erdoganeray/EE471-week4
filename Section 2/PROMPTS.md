# Section 2: AI Prompts

AI coding tool: **Claude Code** (Claude Opus 5.5)

## Part 1: Figma design through the Figma MCP server

Setup:

1. I activated the free Figma **Education** plan with my student account. Writing to Figma through MCP is not available on the free Starter plan.
2. I connected the remote Figma MCP server to Claude Code with `claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp` and signed in to Figma with `/mcp`.
3. Claude Code created a new design file in my Education team and built the design there through the MCP server, using the prompt below.

### Prompt 1: Design the library app in Figma

> Design a single-page library web app in a new Figma file. Use Auto Layout everywhere and put everything in one section named "Library App".
>
> - Make an "Item Card" component with two variants, `Status=Available` and `Status=Checked out`. It shows the title, author, a Book/DVD badge, the page count or duration, an availability badge, a Checkout/Return button and edit and delete icon buttons.
> - Create a "Main" screen with an "Available only" toggle, an All / Books / DVDs filter, a "+ Add Item" button, an error message area ("Cannot delete a checked-out item.") and six item cards, books and DVDs, two of them checked out.
> - Create an "Empty State" screen that shows "No items yet" instead of the list.
> - Create an add/edit form with title, author, a media type dropdown and a length field that switches between "Page Count" (Book) and "Duration (min)" (DVD). Show an "Add Item – Book" and an "Edit Item – DVD" version.
> - Use the Inter font, a light gray page background, white cards and a dark navy primary color.

**Result:** The design in [EE471 Week4 Library App](https://www.figma.com/design/CZhIb4XToB6VuuPTPXXuTc/EE471-Week4-Library-App?node-id=0-1&t=lWF3u6F5ut9POitO-1), exported as `design/library.png`.

## Part 2: Extend the classes with CRUD methods

### Prompt 2: Add CRUD methods to the Week 3 classes

> Copy `custom_classes.py` and `main.py` from the `EE471-week3` submodule into `Section 2/` and extend them with CRUD methods. Keep the existing code and style; change only what the tasks require.
>
> - In `custom_classes.py`, add `ItemNotFoundError` and `ItemStateError`.
> - `LibraryCollection.add_item()` gives every item a unique integer id (1, 2, 3, ...) and returns it. Ids are never reused, even after a delete.
> - Add `to_dict()` to `MediaItem` (id, type, title, author, is_available) and override it in `Book` and `DVD` to add `page_count` or `duration`. Use `"book"` and `"dvd"` as the type.
> - `checkout()` raises `ItemStateError` when the item is already out, and `return_item()` raises it when the item is not checked out. `DVD.checkout()` returns the care reminder in its success message instead of printing it.
> - Add `get_item(item_id)`, `list_items(available=None, item_type=None)`, `update_item(item_id, **fields)` and `remove_item(item_id)` to `LibraryCollection`. Only title, author, page_count and duration can be updated; changing id, type or is_available raises `ValueError`. Removing a checked-out item raises `ItemStateError`.
> - Rewrite `main.py` so it calls every method once and triggers each exception, catching them with try/except.

**Result:** `custom_classes.py` and `main.py` in `Section 2/`. The Week 3 code and docstrings were kept; only the parts the tasks required were changed. Running `python main.py` calls every method and catches `ItemNotFoundError`, `ItemStateError` and `ValueError`.

## Part 3: Flask REST API

### Prompt 3: Expose the LibraryCollection through a REST API

> Create `Section 2/app.py`, a Flask REST API for one `LibraryCollection` seeded with at least 3 items of mixed types, and `Section 2/requirements.txt` with `flask`. Keep it simple.
>
> - Endpoints: `POST /api/items` (201), `GET /api/items` with `?available=true` and `?type=book` filters, `GET`, `PUT`, `PATCH` and `DELETE /api/items/<id>` (DELETE returns 204), `POST /api/items/<id>/checkout` and `POST /api/items/<id>/return`.
> - Every response is JSON; errors are `{"error": "<message>"}`. Map `ValueError` to 400, `ItemNotFoundError` to 404 and `ItemStateError` to 409.
> - The routes only translate HTTP to method calls. All rules stay in `custom_classes.py`: add the methods that are missing there (creating a Book or DVD from request fields, replacing all editable fields for PUT) and validate the values (non-empty title and author, positive whole numbers for page_count and duration).

**Result:** `app.py` and `requirements.txt` in `Section 2/`. `custom_classes.py` got `create_item()`, `replace_item()` and value checks for new and updated fields.
