---
policy_id: FRAUD-002
title: OTP Leak Handling
intent: ACCOUNT_SECURITY
urgency_applicability: ["HIGH", "CRITICAL"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Risk Operations"
---

## Khi áp dụng
Áp dụng khi khách hàng thừa nhận đã lộ OTP, mã xác thực, hoặc nghi ngờ có người khác đã dùng OTP để thực hiện giao dịch.

## SLA
CRITICAL phải được tiếp nhận ngay lập tức và escalte giám sát viên trong 5 phút.

## Thông tin cần hỏi
Hỏi thời điểm lộ OTP, kênh lộ thông tin, giao dịch bất thường đã phát sinh chưa, thiết bị đăng nhập hiện tại, và khách hàng đã đổi mật khẩu hay khóa thẻ chưa.

## Các bước xử lý nội bộ
Đánh dấu rủi ro tài khoản, kích hoạt quy trình khóa kênh đăng nhập nếu phù hợp, ưu tiên tra soát giao dịch gần nhất, và chuyển Risk Operations cùng Supervisor nếu có giao dịch lạ.

## Không được làm
Không yêu cầu khách hàng gửi lại OTP. Không hướng dẫn tiếp tục giao dịch khi nghi ngờ tài khoản đã bị chiếm quyền. Không để ticket tự động gửi ra ngoài.

## Mẫu phản hồi nội bộ
Khách hàng báo lộ OTP, cần khóa rủi ro và kiểm tra giao dịch liên quan ngay theo quy trình an ninh tài khoản.
