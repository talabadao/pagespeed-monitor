"""
PageSpeed Insights Multi-URL Monitor
--------------------------------------
Tự động kiểm tra tốc độ nhiều trang cùng lúc bằng Google PageSpeed Insights API v5.
Lưu kết quả vào:
  - reports/raw/  → từng file JSON theo timestamp
  - reports/summary.csv → tổng hợp tất cả lần chạy (append)

Cách dùng:
  python pagespeed_checker.py --key YOUR_API_KEY --strategy both \
    --url https://example.com \
    --url https://example.com/product/ \
    --url https://example.com/category/

Hoặc dùng file config URLs:
  python pagespeed_checker.py --key YOUR_API_KEY --urls-file urls.txt

Hoặc set biến môi trường:
  PSI_API_KEY, PSI_URLS (dấu phẩy phân cách)
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

# ─── CẤU HÌNH ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
REPORT_DIR = BASE_DIR / "reports"
RAW_DIR    = REPORT_DIR / "raw"
CSV_PATH   = REPORT_DIR / "summary.csv"

PSI_ENDPOINT  = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
API_TIMEOUT   = 120   # giây — tăng lên để tránh timeout cho trang nặng
MAX_RETRIES   = 3     # số lần retry khi gặp timeout/lỗi mạng
RETRY_DELAY   = 15    # giây chờ giữa mỗi lần retry

CSV_HEADERS = [
    "timestamp", "url", "strategy",
    "performance_score",
    "fcp_ms", "lcp_ms", "cls", "tbt_ms", "speed_index_ms", "tti_ms",
    "field_fcp_ms", "field_lcp_ms", "field_cls", "field_inp_ms", "field_ttfb_ms",
    "status",
]

# ─── API ──────────────────────────────────────────────────────────────────────

def fetch_psi(url: str, api_key: str, strategy: str = "mobile") -> dict:
    """Gọi PSI API với retry tự động khi gặp timeout hoặc lỗi mạng."""
    params = urllib.parse.urlencode({
        "url": url,
        "key": api_key,
        "strategy": strategy,
        "category": "performance",
    })
    full_url = f"{PSI_ENDPOINT}?{params}"

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(full_url, timeout=API_TIMEOUT) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: {body[:300]}")  # lỗi API thì không retry
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                print(f"       ⚠ Attempt {attempt}/{MAX_RETRIES} failed: {e}")
                print(f"       → Retry sau {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"       ✗ Tất cả {MAX_RETRIES} lần thử đều thất bại.")

    raise RuntimeError(f"After {MAX_RETRIES} retries: {last_error}")


def extract_metrics(data: dict) -> dict:
    cats  = data.get("lighthouseResult", {}).get("categories", {})
    auds  = data.get("lighthouseResult", {}).get("audits", {})
    items = auds.get("metrics", {}).get("details", {}).get("items", [{}])
    m     = items[0] if items else {}
    lexp  = data.get("loadingExperience", {}).get("metrics", {})

    score = cats.get("performance", {}).get("score")
    return {
        "performance_score": round(score * 100) if score is not None else None,
        "fcp_ms":            m.get("firstContentfulPaint"),
        "lcp_ms":            m.get("largestContentfulPaint"),
        "cls":               m.get("cumulativeLayoutShift"),
        "tbt_ms":            m.get("totalBlockingTime"),
        "speed_index_ms":    m.get("speedIndex"),
        "tti_ms":            m.get("interactive"),
        "field_fcp_ms":      lexp.get("FIRST_CONTENTFUL_PAINT_MS",      {}).get("percentile"),
        "field_lcp_ms":      lexp.get("LARGEST_CONTENTFUL_PAINT_MS",     {}).get("percentile"),
        "field_cls":         lexp.get("CUMULATIVE_LAYOUT_SHIFT_SCORE",   {}).get("percentile"),
        "field_inp_ms":      lexp.get("INTERACTION_TO_NEXT_PAINT",       {}).get("percentile"),
        "field_ttfb_ms":     lexp.get("EXPERIMENTAL_TIME_TO_FIRST_BYTE", {}).get("percentile"),
    }


# ─── LƯU FILE ─────────────────────────────────────────────────────────────────

def slug(url: str) -> str:
    """Rút gọn URL thành tên file an toàn."""
    s = url.replace("https://", "").replace("http://", "")
    s = s.rstrip("/").replace("/", "__").replace(".", "-")
    return s[:60]


def save_raw(data: dict, timestamp: str, url: str, strategy: str):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    fname = RAW_DIR / f"{timestamp}_{slug(url)}_{strategy}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return fname.name


def append_csv(row: dict):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    write_header = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


# ─── CORE ─────────────────────────────────────────────────────────────────────

def check_one(url: str, api_key: str, strategy: str, timestamp: str) -> dict:
    """Kiểm tra một URL / strategy. Trả về dict kết quả."""
    print(f"  [{strategy.upper()}] {url}")
    status  = "ok"
    metrics = {}
    try:
        raw     = fetch_psi(url, api_key, strategy)
        metrics = extract_metrics(raw)
        fname   = save_raw(raw, timestamp, url, strategy)

        score = metrics.get("performance_score")
        lcp   = metrics.get("lcp_ms")
        fcp   = metrics.get("fcp_ms")
        cls_v = metrics.get("cls")
        print(f"       Score={score}  FCP={fcp}ms  LCP={lcp}ms  CLS={cls_v}")
        print(f"       → raw saved: {fname}")

    except Exception as e:
        status = f"error: {e}"
        print(f"       ✗ ERROR: {e}")

    row = {
        "timestamp": timestamp,
        "url":       url,
        "strategy":  strategy,
        "status":    status,
        **{k: metrics.get(k, "") for k in CSV_HEADERS
           if k not in ("timestamp", "url", "strategy", "status")},
    }
    append_csv(row)
    return row


def run_all(urls: list[str], api_key: str, strategies: list[str]):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    total     = len(urls) * len(strategies)

    print(f"\n{'='*65}")
    print(f"  PageSpeed Monitor — {timestamp}")
    print(f"  URLs: {len(urls)}  |  Strategies: {strategies}  |  Total calls: {total}")
    print(f"{'='*65}")

    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        for strategy in strategies:
            row = check_one(url, api_key, strategy, timestamp)
            results.append(row)
            if total > 1:
                time.sleep(1)   # tránh rate-limit

    print(f"\n{'─'*65}")
    print(f"✓ Xong! {len(results)} kết quả → {CSV_PATH}")
    print(f"  Raw JSONs  → {RAW_DIR}")
    print(f"{'─'*65}\n")
    return results


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PageSpeed Insights multi-URL monitor")
    parser.add_argument("--key",      default=os.environ.get("PSI_API_KEY", ""),
                        help="Google API key (hoặc env PSI_API_KEY)")
    parser.add_argument("--url",      action="append", dest="urls", default=[],
                        help="URL cần kiểm tra (có thể lặp lại nhiều lần)")
    parser.add_argument("--urls-file", default="",
                        help="File text chứa danh sách URL, mỗi dòng một URL")
    parser.add_argument("--strategy",  default="both",
                        choices=["mobile", "desktop", "both"],
                        help="Chiến lược kiểm tra (mặc định: both)")
    args = parser.parse_args()

    # Gom URLs từ --url, --urls-file, và env
    urls = list(args.urls)
    if args.urls_file and Path(args.urls_file).exists():
        with open(args.urls_file, encoding="utf-8") as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    env_urls = os.environ.get("PSI_URLS", "")
    if env_urls:
        urls += [u.strip() for u in env_urls.split(",") if u.strip()]

    if not urls:
        print("ERROR: Chưa có URL. Dùng --url hoặc --urls-file hoặc env PSI_URLS")
        sys.exit(1)
    if not args.key:
        print("ERROR: Thiếu API key. Dùng --key hoặc env PSI_API_KEY")
        sys.exit(1)

    strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]
    run_all(urls, args.key, strategies)


if __name__ == "__main__":
    main()
