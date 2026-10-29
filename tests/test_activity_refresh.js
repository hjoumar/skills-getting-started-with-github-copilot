const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.listeners = {};
    this.value = "";
    this.classList = { remove() {}, add() {} };
  }

  appendChild(child) { this.children.push(child); }
  set innerHTML(value) { this.html = value; this.children = []; }
  set length(value) { this.children.length = value; }
  setAttribute() {}
  addEventListener(event, callback) { this.listeners[event] = callback; }
  reset() {}
}

function setup() {
  const elements = Object.fromEntries(
    ["activities-list", "activity", "signup-form", "message", "email"]
      .map((id) => [id, new Element()])
  );
  elements.activity.appendChild(new Element("option"));
  elements.activity.value = "Chess Club";
  elements.email.value = "new@example.com";
  const requests = [];
  let initialize;
  vm.runInNewContext(
    fs.readFileSync(path.join(__dirname, "..", "src", "static", "app.js"), "utf8"),
    {
      document: {
        getElementById: (id) => elements[id],
        createElement: (tag) => new Element(tag),
        addEventListener: (event, callback) => { initialize = callback; },
      },
      fetch: (url, options) => {
        if (options?.method === "POST") {
          return Promise.resolve({
            ok: true,
            json: async () => ({ message: "Signed up" }),
          });
        }
        return new Promise((resolve, reject) => requests.push({ resolve, reject }));
      },
      console: { error() {} },
      setTimeout() {},
    }
  );
  initialize();
  return { elements, requests };
}

function respond(request, participants) {
  request.resolve({
    ok: true,
    json: async () => ({
      "Chess Club": {
        description: "Chess",
        schedule: "Fridays",
        max_participants: 12,
        participants,
      },
    }),
  });
}

const settle = () => new Promise((resolve) => setImmediate(resolve));

function assertUpdated(elements) {
  const card = elements["activities-list"].children[0];
  assert.ok(card.html.includes("11 spots left"));
  const section = card.children[0];
  assert.equal(section.children[0].textContent, "Participants (1)");
  assert.equal(
    section.children[1].children[0].children[0].textContent,
    "new@example.com"
  );
  assert.equal(elements.activity.children.length, 2);
}

test("signup refreshes the participant list and availability without reloading", async () => {
  const { elements, requests } = setup();
  respond(requests[0], []);
  await settle();
  const submitted = elements["signup-form"].listeners.submit({ preventDefault() {} });
  await settle();
  respond(requests[1], ["new@example.com"]);
  await submitted;
  assertUpdated(elements);
});

test("a late initial response cannot overwrite the post-signup refresh", async () => {
  const { elements, requests } = setup();
  const submitted = elements["signup-form"].listeners.submit({ preventDefault() {} });
  await settle();
  respond(requests[1], ["new@example.com"]);
  await submitted;
  respond(requests[0], []);
  await settle();
  assertUpdated(elements);
});

test("an obsolete failed request cannot replace refreshed cards with an error", async () => {
  const { elements, requests } = setup();
  const submitted = elements["signup-form"].listeners.submit({ preventDefault() {} });
  await settle();
  respond(requests[1], ["new@example.com"]);
  await submitted;
  requests[0].reject(new Error("Old request failed"));
  await settle();
  assertUpdated(elements);
});
