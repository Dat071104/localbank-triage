---
policy_id: CARD-002
title: ATM Swallowed Card Handling
intent: CARD_ISSUE
urgency_applicability: ["MEDIUM", "HIGH"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Card Operations"
---

## Khi áp dụng
Áp dụng khi thẻ bị ATM nuốt hoặc giữ lại trong quá trình giao dịch.

## SLA
Tiếp nhận trong 30 phút. Nếu ATM ở ngoài mạng lưới hoặc có trừ tiền bất thường thì nâng mức ưu tiên.

## Thông tin cần hỏi
Hỏi địa điểm ATM, thời gian sự cố, giao dịch trước khi bị nuốt thẻ, và ATM có biên nhận lỗi hay không.

## Các bước xử lý nội bộ
Tạo yêu cầu tra soát ATM, hướng dẫn khóa thẻ tạm thời nếu cần, và phối hợp đơn vị vận hành ATM để truy hồi hoặc phát hành lại.

## Không được làm
Không yêu cầu khách hàng đứng chờ tại ATM quá lâu. Không cam kết lấy lại thẻ trong ngày nếu chưa có xác nhận từ đơn vị vận hành.

## Mẫu phản hồi nội bộ
Đã ghi nhận sự cố ATM nuốt thẻ, chuyển Card Operations tra soát và hướng dẫn khóa thẻ tạm thời nếu cần.
