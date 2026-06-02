---
policy_id: APP-001
title: Mobile Banking Crash Response
intent: MOBILE_APP_ERROR
urgency_applicability: ["LOW", "MEDIUM", "HIGH"]
version: "2026-01"
effective_date: "2026-01-01"
owner: "Digital Banking"
---

## Khi áp dụng
Áp dụng khi ứng dụng mobile banking bị treo, văng ra, hoặc không hoàn tất thao tác nhưng chưa có bằng chứng mất tiền.

## SLA
MEDIUM trong 1 giờ. Nếu lỗi ảnh hưởng thanh toán diện rộng thì nâng lên HIGH và thông báo kỹ thuật.

## Thông tin cần hỏi
Hỏi phiên bản app, loại thiết bị, thao tác đang thực hiện, ảnh chụp lỗi nếu có, và mức độ ảnh hưởng lặp lại.

## Các bước xử lý nội bộ
Ghi nhận mã lỗi, đối chiếu incident đang mở, hướng dẫn cập nhật ứng dụng hoặc thử lại an toàn, và chuyển đội kỹ thuật nếu lỗi lặp lại.

## Không được làm
Không hướng dẫn gỡ bảo mật thiết bị. Không hứa thời gian fix khi chưa có xác nhận từ đội kỹ thuật.

## Mẫu phản hồi nội bộ
Đã ghi nhận sự cố ứng dụng mobile banking, kiểm tra lỗi hiện tại và chuyển kỹ thuật nếu cần.
