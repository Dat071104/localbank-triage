---
policy_id: LOAN-001
title: Loan Status Inquiry
intent: LOAN_SUPPORT
urgency_applicability: ["LOW", "MEDIUM"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Loan Operations"
---

## Khi áp dụng
Áp dụng khi khách hàng hỏi về trạng thái hồ sơ vay, lịch giải ngân, hoặc tiến độ thẩm định.

## SLA
LOW trong 1 ngày làm việc, MEDIUM trong 4 giờ làm việc nếu gần hạn giải ngân.

## Thông tin cần hỏi
Hỏi mã hồ sơ vay, sản phẩm vay, chi nhánh xử lý, và mốc thời gian khách hàng được hẹn phản hồi.

## Các bước xử lý nội bộ
Tra cứu trạng thái hồ sơ, đối chiếu checklist còn thiếu, liên hệ Loan Operations hoặc chi nhánh phụ trách nếu cần.

## Không được làm
Không cam kết phê duyệt khoản vay. Không chia sẻ đánh giá nội bộ chưa được phép công bố.

## Mẫu phản hồi nội bộ
Đã ghi nhận yêu cầu tra cứu hồ sơ vay, đang kiểm tra tiến độ với đơn vị xử lý liên quan.
