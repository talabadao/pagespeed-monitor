# 📊 PageSpeed Insights — wewine.vn Daily Monitor

Tự động kiểm tra tốc độ website **wewine.vn** mỗi ngày bằng GitHub Actions + Google PageSpeed Insights API v5, trên cả **Mobile** và **Desktop**.

## URLs đang theo dõi

| Trang | URL |
|-------|-----|
| Trang chủ | https://wewine.vn/ |
| Blog | https://wewine.vn/cac-vung-ruou-vang-phap-noi-tieng-nhat/ |
| Danh mục sản phẩm | https://wewine.vn/quoc-gia/phap/ |
| Trang sản phẩm | https://wewine.vn/michele-chiarlo-montemareto-nizza/ |

## Lịch chạy

GitHub Actions chạy 1 lần/ngày (xem `.github/workflows/pagespeed.yml`), kiểm tra cả 4 trang × 2 strategy (mobile + desktop) = 8 request/ngày.

## Kết quả

- 📄 **`reports/summary.csv`** — Tổng hợp tất cả lần chạy (mở bằng Excel/Google Sheets)
- 📁 **`reports/raw/`** — JSON chi tiết từng lần (giữ 30 ngày gần nhất)
- 🖥️ **Dashboard** — `docs/index.html` (GitHub Pages) hiển thị điểm số, độ ổn định và xu hướng theo thời gian cho từng trang

## Chỉ số theo dõi

| Chỉ số | Tốt | Cần cải thiện | Kém |
|--------|-----|--------------|-----|
| Performance Score | ≥ 90 | 50–89 | < 50 |
| FCP | ≤ 1,800ms | ≤ 3,000ms | > 3,000ms |
| LCP | ≤ 2,500ms | ≤ 4,000ms | > 4,000ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| TTI | ≤ 3,800ms | ≤ 7,300ms | > 7,300ms |
