---
policy_id: ACC-002
title: Locked Account Handling
intent: ACCOUNT_ACCESS
urgency_applicability: ["MEDIUM", "HIGH"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Digital Banking"
---

## Khi áp dụng
Áp dụng khi tài khoản bị khóa do nhập sai nhiều lần, nghi ngờ bất thường, hoặc bị khóa bởi quy trình rủi ro.

## SLA
MEDIUM trong 1 giờ, HIGH trong 15 phút nếu khách hàng không thể truy cập tài khoản đang có giao dịch chờ xử lý.

## Thông tin cần hỏi
Xác minh thời điểm khóa, thao tác trước khi bị khóa, thông báo nhận được, và kênh đăng nhập bị ảnh hưởng.

## Các bước xử lý nội bộ
Kiểm tra lý do khóa, xác minh danh tính, phối hợp đội Digital Banking hoặc Risk tùy nguyên nhân, và mở khóa theo đúng thẩm quyền.

## Không được làm
Không mở khóa chỉ theo yêu cầu miệng. Không bỏ qua tín hiệu gian lận khi tài khoản bị khóa do rủi ro.

## Mẫu phản hồi nội bộ
Đã ghi nhận tài khoản bị khóa, đang xác minh nguyên nhân và chuyển đội phù hợp để xử lý mở khóa an toàn.
