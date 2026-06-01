# 📊 PageSpeed Insights — Weekly Monitor

Tự động kiểm tra tốc độ website **mỗi giờ** bằng GitHub Actions + Google PageSpeed Insights API v5.

## URLs đang theo dõi

| Trang | URL |
|-------|-----|
| Homepage | https://samuelw86.sg-host.com/ |
| Product  | https://samuelw86.sg-host.com/michele-chiarlo-montemareto-nizza/ |
| Category | https://samuelw86.sg-host.com/quoc-gia/phap/ |
| Blog     | https://samuelw86.sg-host.com/cac-vung-ruou-vang-phap-noi-tieng-nhat/ |

## Kết quả

- 📄 **`reports/summary.csv`** — Tổng hợp tất cả lần chạy (mở bằng Excel/Google Sheets)
- 📁 **`reports/raw/`** — JSON chi tiết từng lần (giữ 7 ngày gần nhất)

## Chỉ số theo dõi

| Chỉ số | Tốt | Cần cải thiện | Kém |
|--------|-----|--------------|-----|
| Performance Score | ≥ 90 | 50–89 | < 50 |
| FCP | ≤ 1,800ms | ≤ 3,000ms | > 3,000ms |
| LCP | ≤ 2,500ms | ≤ 4,000ms | > 4,000ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| TTI | ≤ 3,800ms | ≤ 7,300ms | > 7,300ms |
