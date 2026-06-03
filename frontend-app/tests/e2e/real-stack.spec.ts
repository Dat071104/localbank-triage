import { expect, test } from "@playwright/test";

test.describe("real backend stack smoke", () => {
  test.skip(process.env.E2E_REAL_STACK !== "1", "Set E2E_REAL_STACK=1 and VITE_API_MODE=real to run against the local backend stack.");

  test("CS_AGENT creates analyzes and is blocked from approving a CRITICAL ticket", async ({ page }) => {
    const ticketText = `REAL_SMOKE_${Date.now()} Khach bao lo OTP va co giao dich 10 trieu khong hop le.`;

    await page.goto("/");
    await page.getByRole("button", { name: "Vào không gian xử lý" }).click();
    await expect(page.getByRole("heading", { name: "Hàng đợi ticket" })).toBeVisible();
    await expect(page.getByText("Chế độ: real")).toBeVisible();

    await page.getByLabel("Ticket khách hàng mới").fill(ticketText);
    await page.getByRole("button", { name: "Tạo ticket" }).click();
    await page.getByRole("button", { name: "Phân tích và tạo bản nháp" }).click();

    await expect(page.getByText(/CRITICAL/i)).toBeVisible({ timeout: 25_000 });
    await expect(page.getByLabel("Trình soạn bản nháp")).toBeVisible();
    await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeDisabled();
    await expect(page.getByRole("button", { name: "Yêu cầu supervisor duyệt" })).toBeVisible();

    await page.getByRole("button", { name: "Trạng thái hệ thống" }).click();
    await expect(page.getByText("auth-service", { exact: true })).toBeVisible();
    await expect(page.getByText("api-gateway", { exact: true })).toBeVisible();
  });
});
