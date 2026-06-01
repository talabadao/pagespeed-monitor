# Hướng dẫn: Tự động kiểm tra tốc độ Website mỗi giờ bằng Claude Cowork

> **Mục tiêu:** Chạy PageSpeed Insights API mỗi giờ trong 1 tuần, lưu báo cáo để theo dõi sự ổn định tốc độ website.

---

## BƯỚC 1 — Lấy Google PageSpeed Insights API Key

### 1.1 Tạo Project trên Google Cloud

1. Vào **[Google Cloud Console](https://console.cloud.google.com/)**
2. Bấm **"Select a project"** → **"New Project"**
3. Đặt tên project (ví dụ: `pagespeed-monitor`) → **"Create"**

### 1.2 Bật PageSpeed Insights API

1. Trong Cloud Console, vào menu **"APIs & Services"** → **"Library"**
2. Tìm kiếm **"PageSpeed Insights API"**
3. Bấm vào kết quả → **"Enable"**

### 1.3 Tạo API Key

1. Vào **"APIs & Services"** → **"Credentials"**
2. Bấm **"+ Create Credentials"** → **"API key"**
3. API key sẽ hiện ra — **copy lại ngay**
4. *(Khuyến nghị)* Bấm **"Restrict Key"** → giới hạn chỉ cho PageSpeed Insights API để bảo mật

> **Lưu ý:** API key miễn phí cho phép **25.000 request/ngày** — kiểm tra mỗi giờ (2 strategy × 24h) chỉ dùng **48 request/ngày**, hoàn toàn trong giới hạn free tier.

---

## BƯỚC 2 — Chuẩn bị Script

File `pagespeed_checker.py` đã có sẵn trong folder này. Script này:

- Gọi PSI API cho cả **mobile** và **desktop**
- Lưu JSON thô vào `reports/raw/YYYYMMDDTHHMMSSZ_mobile.json`
- Ghi tổng hợp vào `reports/summary.csv` (append mỗi giờ)
- Trích xuất các chỉ số: Performance Score, FCP, LCP, CLS, TBT, INP, TTFB

### Thử chạy tay một lần

Mở terminal, `cd` vào folder này rồi chạy:

```bash
python pagespeed_checker.py \
  --url https://your-website.com \
  --key YOUR_API_KEY_HERE \
  --strategy both
```

Nếu thành công, bạn sẽ thấy output dạng:

```
============================================================
PageSpeed check @ 20240601T083000Z
URL: https://your-website.com
============================================================

[MOBILE]
  Performance score : 78
  FCP (lab)         : 1850 ms
  LCP (lab)         : 2900 ms
  CLS               : 0.05
  TBT               : 120 ms
  LCP (field/CrUX)  : 2400 ms
  [raw] saved → 20240601T083000Z_mobile.json
  [csv] appended → summary.csv
```

---

## BƯỚC 3 — Thiết lập Scheduled Task trong Claude Cowork

Đây là bước quan trọng nhất — dùng Claude Cowork để **tự động chạy script mỗi giờ**.

### 3.1 Mở Claude Desktop (Cowork mode)

Đảm bảo bạn đang trong **Cowork session** với folder `Page Speed Insight` đã được mount.

### 3.2 Yêu cầu Claude tạo scheduled task

Paste đoạn prompt sau vào chat với Claude:

```
Hãy tạo một scheduled task chạy mỗi giờ để kiểm tra tốc độ website với lệnh sau:

python "C:\Users\HP VICTUS\OneDrive\문서\Claude\Projects\Page Speed Insight\pagespeed_checker.py" --url https://YOUR-WEBSITE.com --key YOUR_API_KEY --strategy both

Scheduled task này chạy lúc đầu giờ mỗi giờ (cron: 0 * * * *)
```

> Thay `https://YOUR-WEBSITE.com` và `YOUR_API_KEY` bằng giá trị thực của bạn.

### 3.3 Xác nhận scheduled task

Claude sẽ hiện task đã tạo. Bạn có thể kiểm tra bằng cách hỏi:

```
Liệt kê tất cả scheduled tasks đang chạy
```

---

## BƯỚC 4 — Xem Báo cáo

### File báo cáo

Sau khi chạy, folder `reports/` sẽ có cấu trúc:

```
reports/
├── summary.csv          ← Tổng hợp tất cả lần chạy (mở bằng Excel)
└── raw/
    ├── 20240601T080000Z_mobile.json
    ├── 20240601T080000Z_desktop.json
    ├── 20240601T090000Z_mobile.json
    └── ...
```

### Cột trong summary.csv

| Cột | Ý nghĩa |
|-----|---------|
| `timestamp` | Thời điểm kiểm tra (UTC) |
| `performance_score` | Điểm hiệu suất tổng (0–100) |
| `fcp_ms` | First Contentful Paint (lab, ms) |
| `lcp_ms` | Largest Contentful Paint (lab, ms) |
| `cls` | Cumulative Layout Shift |
| `tbt_ms` | Total Blocking Time (ms) |
| `field_lcp_ms` | LCP từ dữ liệu người dùng thực (CrUX) |
| `field_inp_ms` | Interaction to Next Paint (CrUX) |
| `field_ttfb_ms` | Time to First Byte (CrUX) |

### Phân tích báo cáo

Sau 1 tuần (168 data points mỗi strategy), bạn có thể yêu cầu Claude phân tích:

```
Đọc file reports/summary.csv và phân tích:
1. Xu hướng Performance Score theo thời gian
2. Các giờ trong ngày website chậm nhất
3. So sánh mobile vs desktop
4. Phát hiện bất thường (spike đột ngột)
```

---

## NGƯỠNG ĐÁNH GIÁ (theo Google)

| Chỉ số | Tốt | Cần cải thiện | Kém |
|--------|-----|--------------|-----|
| Performance Score | ≥ 90 | 50–89 | < 50 |
| FCP | ≤ 1,800ms | ≤ 3,000ms | > 3,000ms |
| LCP | ≤ 2,500ms | ≤ 4,000ms | > 4,000ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| INP | ≤ 200ms | ≤ 500ms | > 500ms |
| TTFB | ≤ 800ms | ≤ 1,800ms | > 1,800ms |

---

## XỬ LÝ SỰ CỐ

**Lỗi `HTTP 400` hoặc `keyInvalid`**
→ API key sai hoặc chưa bật PageSpeed Insights API trong Cloud Console.

**Lỗi `dailyLimitExceeded`**
→ Vượt 25,000 request/ngày (rất khó xảy ra với lịch mỗi giờ).

**Không có field data (CrUX)**
→ Website chưa có đủ traffic thực, các cột `field_*` sẽ trống — bình thường.

**Script không chạy tự động**
→ Kiểm tra Python đã được cài và có trong PATH: `python --version`
→ Trên Windows có thể cần dùng `python3` thay vì `python`

---

*Tạo bởi Claude Cowork — June 2026*
