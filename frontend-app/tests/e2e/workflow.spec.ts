import { expect, Locator, Page, test } from "@playwright/test";

async function login(page: Page, role: string) {
  await page.goto("/");
  await page.getByRole("button", { name: role.replace("_", " ") }).click();
  await page.getByRole("button", { name: "Vào không gian xử lý" }).click();
  await expect(page.getByRole("heading", { name: "Hàng đợi ticket" })).toBeVisible();
}

function ticketRow(page: Page, ticketId: string): Locator {
  return page.locator(".ticket-row").filter({ hasText: ticketId });
}

async function openTicket(page: Page, ticketId: string) {
  await ticketRow(page, ticketId).getByRole("button", { name: "Mở ticket" }).click();
}

test("mock queue shows at least seven diverse tickets", async ({ page }) => {
  await login(page, "CS_AGENT");
  await expect(page.locator(".ticket-row")).toHaveCount(7);
  await expect(ticketRow(page, "OTP-CRITICAL-001").getByText("RẤT KHẨN CẤP - cần supervisor")).toBeVisible();
  await expect(ticketRow(page, "INFO-LOW-006").getByText("THẤP - thông thường")).toBeVisible();
});

test("CS_AGENT critical OTP approval is blocked and supervisor request is visible", async ({ page }) => {
  await login(page, "CS_AGENT");
  await openTicket(page, "OTP-CRITICAL-001");
  await expect(page.getByText("RẤT KHẨN CẤP - cần supervisor", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Yêu cầu supervisor duyệt" })).toBeVisible();
});

test("SUPERVISOR can approve CRITICAL ticket", async ({ page }) => {
  await login(page, "SUPERVISOR");
  await openTicket(page, "OTP-CRITICAL-001");
  await page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" }).click();
  await expect(page.getByText(/APPROVE đã được ghi nhận/i)).toBeVisible();
  await expect(page.locator(".badge").getByText("ĐÃ DUYỆT", { exact: true })).toBeVisible();
});

test("AUDITOR can view but cannot edit or review", async ({ page }) => {
  await login(page, "AUDITOR");
  await expect(page.getByText("Vai trò AUDITOR chỉ được xem")).toBeVisible();
  await openTicket(page, "OTP-CRITICAL-001");
  await expect(page.getByLabel("Trình soạn bản nháp")).toHaveAttribute("readonly", "");
  await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeDisabled();
});

test("ticket analysis flow shows classifier urgency policy evidence and draft", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByLabel("Ticket khách hàng mới").fill("Khách báo lộ OTP và có giao dịch 10 triệu không hợp lệ.");
  await page.getByRole("button", { name: "Tạo ticket" }).click();
  await page.getByRole("button", { name: "Phân tích và tạo bản nháp" }).click();
  await expect(page.getByText("Đang phân loại ý định...")).toBeVisible();
  await expect(page.getByText("FRAUD_UNAUTHORIZED_TRANSACTION")).toBeVisible();
  await expect(page.locator(".evidence-card").getByText("FRAUD-002", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Trình soạn bản nháp")).toContainText("Cảm ơn");
});

test("service error path shows useful recovery", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByLabel("Ticket khách hàng mới").fill("SERVICE_FAILURE customer text");
  await page.getByRole("button", { name: "Tạo ticket" }).click();
  await page.getByRole("button", { name: "Phân tích và tạo bản nháp" }).click();
  await expect(page.getByRole("alert")).toContainText("Dịch vụ phía sau tạm thời không sẵn sàng");
  await expect(page.getByRole("alert")).toContainText("Kiểm tra classifier");
});

test("mock mode app loads runtime status from clean state", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByRole("button", { name: "Trạng thái hệ thống" }).click();
  await expect(page.getByText("auth-service")).toBeVisible();
  await expect(page.getByText("Đăng nhập demo đang chạy local")).toBeVisible();
});

test("LOW general inquiry can be approved by CS_AGENT", async ({ page }) => {
  await login(page, "CS_AGENT");
  await openTicket(page, "INFO-LOW-006");
  await expect(page.getByText("THẤP - thông thường", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeEnabled();
  await page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" }).click();
  await expect(page.getByText(/APPROVE đã được ghi nhận/i)).toBeVisible();
});

test("no policy context shows manual review and blocks approval", async ({ page }) => {
  await login(page, "SUPERVISOR");
  await openTicket(page, "SAFE-MANUAL-007");
  await expect(page.getByText("Không có chính sách phù hợp")).toBeVisible();
  await expect(page.getByText("NO_POLICY_CONTEXT")).toBeVisible();
  await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeDisabled();
});

test("unsafe fallback draft is flagged and cannot be approved", async ({ page }) => {
  await login(page, "SUPERVISOR");
  await page.getByLabel("Ticket khách hàng mới").fill("unsafe_draft Khách báo lộ OTP và muốn hoàn tiền ngay.");
  await page.getByRole("button", { name: "Tạo ticket" }).click();
  await page.getByRole("button", { name: "Phân tích và tạo bản nháp" }).click();
  await expect(page.getByText("UNSAFE_DRAFT")).toBeVisible();
  await expect(page.getByText("Kiểm tra an toàn bản nháp thất bại")).toBeVisible();
  await expect(page.getByRole("button", { name: "Duyệt bản nháp đã kiểm tra" })).toBeDisabled();
});

test("language toggle switches between VI and EN", async ({ page }) => {
  await login(page, "CS_AGENT");
  await page.getByRole("button", { name: "EN" }).click();
  await expect(page.getByRole("heading", { name: "Ticket Queue" })).toBeVisible();
  await page.getByRole("button", { name: "VI" }).click();
  await expect(page.getByRole("heading", { name: "Hàng đợi ticket" })).toBeVisible();
});

test("empty queue shows useful empty state", async ({ page }) => {
  await login(page, "ADMIN");
  await page.getByRole("button", { name: "Xóa hàng đợi demo" }).click();
  await expect(page.getByText("Không có ticket trong hàng đợi")).toBeVisible();
});
