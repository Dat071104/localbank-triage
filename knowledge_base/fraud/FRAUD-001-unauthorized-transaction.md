---
policy_id: FRAUD-001
title: Unauthorized Transaction Handling
intent: TRANSACTION_PROBLEM
urgency_applicability: ["HIGH", "CRITICAL"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Risk Operations"
---

## Khi áp dụng
Áp dụng khi khách hàng báo bị trừ tiền, chuyển khoản lạ, hoặc có giao dịch thẻ không do khách hàng thực hiện.

## SLA
Tiếp nhận trong 5 phút với ticket CRITICAL và 15 phút với ticket HIGH. Chuyển giám sát viên ngay nếu có dấu hiệu gian lận đang tiếp diễn.

## Thông tin cần hỏi
Xác minh thời điểm phát sinh giao dịch, số tiền, kênh giao dịch, trạng thái khóa thẻ/tài khoản, và việc khách hàng còn giữ thiết bị hay không.

## Các bước xử lý nội bộ
Đánh dấu ticket là nghi ngờ gian lận, kiểm tra lịch sử giao dịch gần nhất, khóa giao dịch rủi ro nếu quy trình nội bộ cho phép, và chuyển nhóm Risk Operations để điều tra.

## Không được làm
Không khẳng định hoàn tiền trước khi có xác minh nội bộ. Không yêu cầu khách hàng cung cấp OTP hoặc mật khẩu. Không trì hoãn escalte khi còn giao dịch bất thường.

## Mẫu phản hồi nội bộ
Đã ghi nhận báo cáo giao dịch không do khách hàng thực hiện, đã chuyển xử lý gian lận ưu tiên cao và yêu cầu kiểm tra giao dịch ngay.
