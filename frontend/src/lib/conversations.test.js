import { readConversations, STORAGE_KEY } from "./conversations";

test("restores conversations saved by the previous JavaScript interface", () => {
  const chats = [
    {
      id: "existing-chat",
      title: "Python",
      messages: [{ role: "user", content: "Bonjour" }],
    },
  ];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
  expect(readConversations()).toEqual(chats);
});

test("ignores invalid storage without breaking the interface", () => {
  localStorage.setItem(STORAGE_KEY, "not json");
  expect(readConversations()).toEqual([]);
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify([{ id: "a", title: "x", messages: [{ role: "system" }] }]),
  );
  expect(readConversations()).toEqual([]);
});
