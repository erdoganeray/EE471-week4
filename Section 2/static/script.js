// Library page logic.
// Every change goes through the Flask API (/api/items). The rules (valid
// values, checkout state, ...) live in custom_classes.py, not here.

const ICONS = {
  book: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/></svg>',
  dvd: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
};

const itemList = document.getElementById("item-list");
const cardTemplate = document.getElementById("card-template");
const emptyState = document.getElementById("empty-state");
const emptyTitle = document.getElementById("empty-title");
const emptyText = document.getElementById("empty-text");
const message = document.getElementById("message");
const messageText = document.getElementById("message-text");
const availableToggle = document.getElementById("available-only");
const typeFilter = document.getElementById("type-filter");

const dialog = document.getElementById("item-dialog");
const form = document.getElementById("item-form");
const formHeading = document.getElementById("form-heading");
const formError = document.getElementById("form-error");
const titleInput = document.getElementById("title-input");
const authorInput = document.getElementById("author-input");
const typeInput = document.getElementById("type-input");
const lengthLabel = document.getElementById("length-label");
const lengthInput = document.getElementById("length-input");

const filters = { available: false, type: "" };
let editingId = null; // id of the item in the form, null when adding a new one

// ---------- API ----------

// Sends a request and returns the JSON answer (null for 204 No Content);
// throws the API's error message
async function api(method, path, body) {
  const options = { method };
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    throw new Error(data.error);
  }
  return data;
}

// ---------- Messages ----------

function showMessage(text, kind) {
  messageText.textContent = text;
  message.className = `message ${kind}`;
  message.hidden = false;
}

function clearMessage() {
  message.hidden = true;
}

// ---------- Item list ----------

async function loadItems() {
  const params = new URLSearchParams();
  if (filters.available) {
    params.set("available", "true");
  }
  if (filters.type) {
    params.set("type", filters.type);
  }
  try {
    renderItems(await api("GET", `/api/items?${params}`));
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function renderItems(items) {
  itemList.replaceChildren(...items.map(createCard));
  emptyState.hidden = items.length > 0;
  const filtered = filters.available || filters.type !== "";
  emptyTitle.textContent = filtered ? "No matching items" : "No items yet";
  emptyText.textContent = filtered ? "No item matches these filters." : "Add your first book or DVD to get started.";
}

function createCard(item) {
  const card = cardTemplate.content.firstElementChild.cloneNode(true);
  const isBook = item.type === "book";
  card.classList.toggle("checked-out", !item.is_available);
  card.querySelector(".title").textContent = item.title;
  card.querySelector(".author").textContent = item.author;
  card.querySelector(".type-badge").textContent = isBook ? "Book" : "DVD";
  card.querySelector(".length-icon").innerHTML = ICONS[item.type];
  card.querySelector(".length").textContent = isBook ? `${item.page_count} pages` : `${item.duration} mins`;

  const status = card.querySelector(".status-badge");
  status.textContent = item.is_available ? "Available" : "Checked out";
  status.classList.add(item.is_available ? "available" : "checked-out");

  const mainAction = card.querySelector(".main-action");
  const action = item.is_available ? "checkout" : "return";
  mainAction.textContent = item.is_available ? "Checkout" : "Return";
  mainAction.classList.add(item.is_available ? "primary" : "secondary");
  mainAction.addEventListener("click", () => runAction("POST", `/api/items/${item.id}/${action}`));

  card.querySelector(".edit").addEventListener("click", () => openForm(item));
  card.querySelector(".delete").addEventListener("click", () => runAction("DELETE", `/api/items/${item.id}`));
  return card;
}

// Runs a checkout, return or delete request, then reloads the list
async function runAction(method, path) {
  try {
    const data = await api(method, path);
    if (data && data.message) {
      showMessage(data.message, "success");
    } else {
      clearMessage(); // DELETE answers 204 without a message
    }
    await loadItems();
  } catch (error) {
    showMessage(error.message, "error");
  }
}

// ---------- Add/Edit form ----------

function openForm(item) {
  editingId = item ? item.id : null;
  formHeading.textContent = item ? "Edit Item" : "Add New Item";
  titleInput.value = item ? item.title : "";
  authorInput.value = item ? item.author : "";
  typeInput.value = item ? item.type : "book";
  typeInput.disabled = Boolean(item); // the API does not allow changing the type
  lengthInput.value = item ? (item.page_count ?? item.duration) : "";
  updateLengthField();
  formError.hidden = true;
  dialog.showModal();
}

// The length field is a page count for books and a duration for DVDs
function updateLengthField() {
  const isBook = typeInput.value === "book";
  lengthLabel.textContent = isBook ? "Page Count" : "Duration (min)";
  lengthInput.placeholder = isBook ? "e.g. 320" : "e.g. 120";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const lengthField = typeInput.value === "book" ? "page_count" : "duration";
  const fields = {
    title: titleInput.value,
    author: authorInput.value,
    [lengthField]: Number(lengthInput.value),
  };
  try {
    if (editingId === null) {
      await api("POST", "/api/items", { type: typeInput.value, ...fields });
    } else {
      await api("PUT", `/api/items/${editingId}`, fields);
    }
    dialog.close();
    clearMessage();
    await loadItems();
  } catch (error) {
    formError.textContent = error.message;
    formError.hidden = false;
  }
});

// ---------- Events ----------

typeInput.addEventListener("change", updateLengthField);
document.getElementById("cancel-button").addEventListener("click", () => dialog.close());
document.getElementById("add-button").addEventListener("click", () => openForm(null));
document.getElementById("empty-add-button").addEventListener("click", () => openForm(null));

availableToggle.addEventListener("change", () => {
  filters.available = availableToggle.checked;
  loadItems();
});

typeFilter.addEventListener("click", (event) => {
  const tab = event.target.closest(".tab");
  if (!tab) {
    return;
  }
  filters.type = tab.dataset.type;
  for (const other of typeFilter.querySelectorAll(".tab")) {
    other.classList.toggle("active", other === tab);
  }
  loadItems();
});

loadItems();
