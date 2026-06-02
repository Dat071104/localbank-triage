---
policy_id: CARD-001
title: Card Lock Request
intent: CARD_ISSUE
urgency_applicability: ["MEDIUM", "HIGH"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Card Operations"
---

## Khi áp dụng
Áp dụng khi khách hàng yêu cầu khóa thẻ vì thất lạc, nghi bị lộ thông tin thẻ, hoặc muốn ngăn giao dịch tiếp tục.

## SLA
Tiếp nhận trong 15 phút. Nếu có giao dịch bất thường kèm theo thì nâng lên HIGH và xử lý ngay.

## Thông tin cần hỏi
Hỏi loại thẻ, thời điểm phát hiện mất thẻ, giao dịch gần nhất do khách hàng thực hiện, và khách hàng đã thử khóa thẻ trên app chưa.

## Các bước xử lý nội bộ
Xác minh khách hàng theo quy trình, khóa thẻ trên hệ thống nếu cần, ghi nhận yêu cầu phát hành lại nếu khách hàng đồng ý.

## Không được làm
Không đọc đầy đủ số thẻ trên kênh hỗ trợ. Không hứa hoàn phí phát hành lại khi chưa có chính sách áp dụng. Không bỏ qua dấu hiệu giao dịch lạ.

## Mẫu phản hồi nội bộ
Đã tiếp nhận yêu cầu khóa thẻ và kiểm tra giao dịch liên quan, chuyển Card Operations xử lý.
