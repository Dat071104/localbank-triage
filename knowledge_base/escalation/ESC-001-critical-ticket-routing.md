---
policy_id: ESC-001
title: Critical Ticket Routing
intent: TRANSACTION_PROBLEM
urgency_applicability: ["CRITICAL"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Service Operations"
---

## Khi áp dụng
Áp dụng cho mọi ticket CRITICAL liên quan gian lận, lộ OTP, mất tiền, hoặc chiếm quyền tài khoản.

## SLA
Escalate giám sát viên trong 5 phút và chuyển đúng đội xử lý ngay sau khi xác minh tối thiểu.

## Thông tin cần hỏi
Hỏi các dữ kiện tối thiểu để phân luồng: dấu hiệu rủi ro, thời gian phát sinh, số tiền, kênh ảnh hưởng, và trạng thái tài khoản hiện tại.

## Các bước xử lý nội bộ
Gắn nhãn CRITICAL, dừng auto-send, thông báo supervisor, chuyển ticket sang luồng manual review, và ưu tiên điều phối Risk hoặc Security.

## Không được làm
Không để ticket CRITICAL đi thẳng sang bản nháp tự động gửi khách hàng. Không hạ mức ưu tiên khi chưa có căn cứ rõ ràng.

## Mẫu phản hồi nội bộ
Ticket đã được gắn CRITICAL và chuyển manual review với supervisor theo chính sách escalation.
