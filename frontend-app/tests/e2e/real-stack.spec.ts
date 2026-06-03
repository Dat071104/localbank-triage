import { expect, test } from "@playwright/test";

test.describe("real backend stack smoke", () => {
  test.skip(process.env.E2E_REAL_STACK !== "1", "Set E2E_REAL_STACK=1 and VITE_API_MODE=real to run against the local backend stack.");

  test("CS_AGENT creates analyzes and is blocked from approving a CRITICAL ticket", async ({ page }) => {
    const ticketText = `REAL_SMOKE_${Date.now()} Khach bao lo OTP va co giao dich 10 trieu khong hop le.`;

    await page.goto("/");
    await page.getByRole("button", { name: "Enter workspace" }).click();
    await expect(page.getByRole("heading", { name: "Ticket Queue" })).toBeVisible();
    await expect(page.getByText("Mode: real")).toBeVisible();

    await page.getByLabel("New customer ticket").fill(ticketText);
    await page.getByRole("button", { name: "Create ticket" }).click();
    await page.getByRole("button", { name: "Analyze and draft" }).click();

    await expect(page.getByText(/CRITICAL/i)).toBeVisible({ timeout: 25_000 });
    await expect(page.getByLabel("Draft editor")).toBeVisible();
    await expect(page.getByRole("button", { name: "Approve reviewed draft" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Request Supervisor Approval" })).toBeVisible();

    await page.getByRole("button", { name: "Runtime Status" }).click();
    await expect(page.getByText("auth-service", { exact: true })).toBeVisible();
    await expect(page.getByText("api-gateway", { exact: true })).toBeVisible();
  });
});
