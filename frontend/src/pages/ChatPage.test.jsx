import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import ChatPage from "./ChatPage";

test("sends with Enter and restores the draft when the server fails", async () => {
  const send = vi.fn().mockResolvedValue(false);
  render(
    <ChatPage
      conversations={{
        active: { id: "chat", messages: [] },
        busy: false,
        error: "",
        send,
      }}
    />,
  );
  const input = screen.getByRole("textbox", { name: "Votre message" });
  await userEvent.type(input, "Bonjour{Enter}");
  await waitFor(() => expect(send).toHaveBeenCalledWith("Bonjour"));
  await waitFor(() => expect(input).toHaveValue("Bonjour"));
});

test("Shift Enter inserts a newline without sending", async () => {
  const send = vi.fn();
  render(
    <ChatPage
      conversations={{
        active: { id: "chat", messages: [] },
        busy: false,
        error: "",
        send,
      }}
    />,
  );
  const input = screen.getByRole("textbox", { name: "Votre message" });
  await userEvent.type(input, "Bonjour{Shift>}{Enter}{/Shift}suite");
  expect(send).not.toHaveBeenCalled();
  expect(input).toHaveValue("Bonjour\nsuite");
});
