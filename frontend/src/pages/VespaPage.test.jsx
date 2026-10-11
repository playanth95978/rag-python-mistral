import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import VespaPage from "./VespaPage";
import { vespaApi } from "../lib/api";

vi.mock("../lib/api", () => ({
  vespaApi: { collections: vi.fn(), documents: vi.fn(), detail: vi.fn() },
}));

test("switches collections, searches and displays the actual embedding dimensions", async () => {
  vespaApi.collections.mockResolvedValue({
    collections: [
      { name: "cv_user", chunks: 3 },
      { name: "job_chunks", chunks: 2 },
    ],
  });
  vespaApi.documents.mockResolvedValue({
    total: 1,
    items: [
      { id: "one", title: "Mon CV", content: "Python", locator: "char:0-6" },
    ],
  });
  vespaApi.detail.mockResolvedValue({
    id: "one",
    fields: {
      title: "Mon CV",
      content: "Python",
      content_embedding: { values: [1, 2, 3] },
    },
  });
  render(<VespaPage />);
  await userEvent.click(await screen.findByRole("button", { name: /Mon CV/ }));
  await userEvent.click(await screen.findByRole("tab", { name: "Embedding" }));
  expect(screen.getByText("coordonnées").parentElement).toHaveTextContent(
    "3 coordonnées",
  );
  await userEvent.type(
    screen.getByRole("textbox", { name: "Rechercher dans le contenu" }),
    "Python",
  );
  await userEvent.click(screen.getByRole("button", { name: "Rechercher" }));
  await waitFor(() =>
    expect(vespaApi.documents).toHaveBeenLastCalledWith(
      "cv_user",
      "Python",
      0,
      expect.anything(),
    ),
  );
  await userEvent.click(
    screen.getByRole("button", { name: /Offres d’emploi/ }),
  );
  await waitFor(() =>
    expect(vespaApi.documents).toHaveBeenLastCalledWith(
      "job_chunks",
      "",
      0,
      expect.anything(),
    ),
  );
});
