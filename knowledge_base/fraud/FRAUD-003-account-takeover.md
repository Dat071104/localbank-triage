---
policy_id: FRAUD-003
title: Account Takeover Response
intent: ACCOUNT_SECURITY
urgency_applicability: ["HIGH", "CRITICAL"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Security Operations"
---

## Khi áp dụng
Áp dụng khi khách hàng báo tài khoản bị hack, đổi thông tin đăng nhập trái phép, hoặc xuất hiện thiết bị lạ chiếm quyền truy cập.

## SLA
CRITICAL trong 5 phút, HIGH trong 15 phút. Luôn cần supervisor xác nhận nếu phát sinh ảnh hưởng giao dịch tài chính.

## Thông tin cần hỏi
Xác minh thời điểm mất quyền truy cập, thông báo thay đổi số điện thoại/email, dấu hiệu đăng nhập lạ, và khách hàng còn truy cập ứng dụng hay không.

## Các bước xử lý nội bộ
Khóa phiên rủi ro, yêu cầu xác minh danh tính theo quy trình nội bộ, kiểm tra thay đổi hồ sơ gần nhất, và escalte Security Operations để xử lý takeover.

## Không được làm
Không reset tài khoản chỉ dựa trên một thông tin đơn lẻ. Không tiết lộ chi tiết điều tra nội bộ. Không bỏ qua cảnh báo thiết bị lạ.

## Mẫu phản hồi nội bộ
Đã ghi nhận dấu hiệu chiếm quyền tài khoản, cần khóa phiên nghi ngờ và xử lý theo quy trình an ninh ngay.
