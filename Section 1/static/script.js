// Calculator page logic.
// The page only collects the input. Every calculation is sent to the Flask
// server (POST /api/calculate), which uses the Calculator class from Mini Project 1.

const display = document.getElementById("display");
const keypad = document.getElementById("keypad");

let current = "0";     // number shown on the display
let previous = null;   // first number, saved when an operator is pressed
let operator = null;   // "+", "-", "*" or "/"
let startNew = false;  // true after an operator or "=": the next digit starts a new number
let error = null;      // error message from the server, if any

// Sends one calculation to the server and returns its JSON answer
async function calculate(a, op, b) {
  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ a: a, operator: op, b: b }),
    });
    return await response.json();
  } catch {
    return { error: "Server not reachable" };
  }
}

function pressDigit(digit) {
  if (startNew) {
    current = "0";
    startNew = false;
    error = null;
  }
  if (digit === ".") {
    if (!current.includes(".")) {
      current += ".";
    }
  } else {
    current = current === "0" ? digit : current + digit;
  }
}

async function pressOperator(op) {
  // 2 + 3 x ... : finish 2 + 3 first
  if (operator && !startNew) {
    await pressEquals();
  }
  if (error) {
    return;
  }
  previous = Number(current);
  operator = op;
  startNew = true;
}

async function pressEquals() {
  if (!operator || startNew) {
    return;
  }
  const answer = await calculate(previous, operator, Number(current));
  if ("error" in answer) {
    error = answer.error;
  } else {
    current = String(answer.result);
  }
  operator = null;
  startNew = true;
}

function render() {
  display.textContent = error ?? current;
  display.classList.toggle("error", error !== null);
}

keypad.addEventListener("click", async (event) => {
  const value = event.target.dataset.value;
  if (!value) {
    return; // clicked between the buttons
  }
  if (value === "=") {
    await pressEquals();
  } else if ("+-*/".includes(value)) {
    await pressOperator(value);
  } else {
    pressDigit(value);
  }
  render();
});
