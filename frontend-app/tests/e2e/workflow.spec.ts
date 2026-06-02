import { expect, Page, test } from "@playwright/test";

async function login(page: Page, role: string) {
  await page.goto("/");
  await page.getByRole("button", { name: role.replace("_", " ") }).click();
  await page.getByRole("button", { name: "Enter workspace" }).click();
  await expect(page.getByRole("heading", { name: "Ticket Queue" })).toBeVisible();
}

test("CS_AGENT critical approval is blocked and supervisor request is visible", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByRole("button", { name: "Open ticket" }).first().click();
  await expect(page.getByText("CRITICAL - supervisor required", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Approve reviewed draft" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Request Supervisor Approval" })).toBeVisible();
});

test("SUPERVISOR can approve CRITICAL ticket", async ({ page }) => {
  await login(page, "SUPERVISOR");
  await page.getByRole("button", { name: "Open ticket" }).first().click();
  await page.getByRole("button", { name: "Approve reviewed draft" }).click();
  await expect(page.getByText(/APPROVE recorded/i)).toBeVisible();
});

test("AUDITOR can view but cannot edit or review", async ({ page }) => {
  await login(page, "AUDITOR");
  await expect(page.getByText("Auditor role is read-only")).toBeVisible();
  await page.getByRole("button", { name: "Open ticket" }).first().click();
  await expect(page.getByLabel("Draft editor")).toHaveAttribute("readonly", "");
  await expect(page.getByRole("button", { name: "Approve reviewed draft" })).toBeDisabled();
});

test("ticket analysis flow shows classifier urgency policy evidence and draft", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByLabel("New customer ticket").fill("Khach bao lo OTP va co giao dich 10 trieu khong hop le.");
  await page.getByRole("button", { name: "Create ticket" }).click();
  await page.getByRole("button", { name: "Analyze and draft" }).click();
  await expect(page.getByText("Classifying intent...")).toBeVisible();
  await expect(page.getByText("FRAUD_UNAUTHORIZED_TRANSACTION")).toBeVisible();
  await expect(page.locator(".evidence-card").getByText("FRAUD-002", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Draft editor")).toContainText("Cam on");
});

test("service error path shows useful recovery", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByLabel("New customer ticket").fill("SERVICE_FAILURE customer text");
  await page.getByRole("button", { name: "Create ticket" }).click();
  await page.getByRole("button", { name: "Analyze and draft" }).click();
  await expect(page.getByRole("alert")).toContainText("downstream service is unavailable");
  await expect(page.getByRole("alert")).toContainText("Retry after checking");
});

test("mock mode app loads runtime status from clean state", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByRole("button", { name: "Runtime Status" }).click();
  await expect(page.getByText("auth-service")).toBeVisible();
  await expect(page.getByText("Mock login is active")).toBeVisible();
});
