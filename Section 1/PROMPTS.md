# Section 1: AI Prompts

AI coding tool: **Claude Code** (Claude Opus 5.5)

## Prompt 1: Turn the Figma design into a web page

> Turn my Figma calculator design (`design/calculator.png`, [Figma](https://www.figma.com/design/hRnuiYD8ZNH0RvK3OD1u9U/Untitled?node-id=1-49&t=yzAbhp5yi4yyd6s0-1)) into a simple working web page with plain HTML, CSS and JavaScript. Create `index.html`, `style.css` and `script.js` in `Section 1/static/`.
>
> - Match the design: blue frame `#0B78D0` with 8 px padding and 6 px gaps, a white 278 × 64 px display, 65 × 45 px buttons (digits `#7A7A7A`, operators and `.` `#A0A0A0`, `=` `#004E99`) and white bold 36 px Inter text. Keep the button order from the design.
> - Use Flexbox to mirror the Figma Auto Layout (frame → display + keypad → rows).
> - Keep the JavaScript simple: digits build a number, an operator saves it, `=` shows the result. Do not use `eval()`. Put the math in one `calculate(a, operator, b)` function so it can later be moved to a Flask API. Show `Error` for division by zero.

**Result:** `index.html`, `style.css` and `script.js` in `Section 1/static/`. The page matches the design and works when `index.html` is opened in a browser.

## Prompt 2: Move the calculations to a Flask server

> Move all calculations to a Flask server running on localhost. Keep it simple.
>
> - Create `Section 1/app.py`. Flask serves the page from `static/` at `/` and exposes `POST /api/calculate`.
> - JSON format: the request is `{"a": 7, "operator": "+", "b": 8}` with `operator` one of `+ - * /`. Success returns `{"result": 15}`. Errors return `{"error": "<message>"}` with status 400.
> - Do the math with the `Calculator` class from Mini Project 1. It lives in the `EE471_MP1_Calculator` Git submodule: import it from there and do not copy or modify it. Extend it in a subclass in `Section 1/web_calculator.py` with a `calculate(a, operator, b)` method that raises clear errors for invalid input (missing or non-numeric numbers, unknown operator) and for division by zero.
> - Do not use `eval()`.
> - In `script.js`, replace the local `calculate()` with a `fetch` request to the API and show the API's error message on the display.
> - Add `Section 1/requirements.txt` with `flask`.

**Result:** `app.py`, `web_calculator.py` and `requirements.txt` in `Section 1/`, and `script.js` now sends every calculation to `POST /api/calculate`. The page is opened at `http://127.0.0.1:5000`.

## Prompt 3: Make long results fit the display

> `1 / 3` returns `0.3333333333` (12 characters). This does not fit the 36 px display and the last digit is cut off. In `WebCalculator.calculate()`, round results to 8 decimal places instead of 10 so that `1 / 3` shows `0.33333333`.

**Result:** `web_calculator.py` now uses `round(result, 8)`. `1 / 3` returns `0.33333333`, which fits the display.

## Prompt 4: Handle numbers outside the float range

> While testing the API with every kind of input, I found two cases that do not return a proper error:
>
> - Dividing an integer with 309+ digits (`{"a": 1000…000, "operator": "/", "b": 1}`) raises `OverflowError` and the server returns `500 Internal Server Error`.
> - `{"a": 1e308, "operator": "*", "b": 10}` returns `200 {"result": Infinity}`, and `NaN` or `Infinity` as input returns `{"result": NaN}`. `Infinity` and `NaN` are not valid JSON.
>
> Fix this in `web_calculator.py` without changing the Mini Project 1 `Calculator`. Reject `NaN`, `Infinity` and integers too large for a float with the existing `a and b must be numbers` error. If the result is not a finite number, return 400 with `{"error": "Result is too large"}`.

**Result:** `is_number()` now also checks `math.isfinite()` and returns `False` for integers too large for a float, and `calculate()` raises `ValueError("Result is too large")` when the result is not finite. Both cases now return 400 with a JSON error message.
