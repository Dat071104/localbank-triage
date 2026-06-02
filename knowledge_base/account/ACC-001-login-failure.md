---
policy_id: ACC-001
title: Login Failure Troubleshooting
intent: ACCOUNT_ACCESS
urgency_applicability: ["LOW", "MEDIUM"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Digital Banking"
---

## Khi áp dụng
Áp dụng khi khách hàng không đăng nhập được ứng dụng hoặc internet banking nhưng không có dấu hiệu chiếm quyền.

## SLA
LOW trong 4 giờ làm việc, MEDIUM trong 1 giờ.

## Thông tin cần hỏi
Hỏi mã lỗi hiển thị, lần đăng nhập cuối thành công, số lần thử đăng nhập, loại thiết bị, và tình trạng kết nối mạng.

## Các bước xử lý nội bộ
Kiểm tra trạng thái tài khoản, reset hướng dẫn đăng nhập nếu đủ điều kiện, xác minh tình trạng khóa do nhập sai nhiều lần.

## Không được làm
Không yêu cầu khách hàng gửi mật khẩu. Không reset thông tin bảo mật khi chưa xác minh danh tính.

## Mẫu phản hồi nội bộ
Đã ghi nhận lỗi đăng nhập, đang kiểm tra trạng thái tài khoản và hướng xử lý phù hợp.
