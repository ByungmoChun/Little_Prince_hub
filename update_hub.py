# -*- coding: utf-8 -*-
"""
어린왕자 허브 배포 폴더 패치 스크립트 (2026-10-15)
사용법: 배포 폴더(index.html 있는 곳)에 이 파일을 넣고 →  python3 update_hub.py
하는 일:
  1) 모든 .html에서 구버전 메뉴 파일명 5종을 신버전으로 치환 (plan/issues/docs 메뉴 404 수리)
  2) index.html 대시보드 상단에 LOA 계약 체결 배너 삽입 (중복 실행해도 1번만)
  3) vercel.json 생성 — 구주소로 공유된 링크도 새 페이지로 리다이렉트
  4) 링크돼 있지만 폴더에 없는 파일 3종 존재 여부 점검
끝나면 폴더째 Vercel에 드래그해서 재배포하면 됩니다.
"""
import glob, io, json, os, sys

RENAMES = {
    "어린왕자_프로젝트_허브.html": "index.html",
    "어린왕자_허브_기획.html": "plan.html",
    "어린왕자_허브_개발범위.html": "scope.html",
    "어린왕자_허브_이슈결정.html": "issues.html",
    "어린왕자_허브_문서.html": "docs.html",
}

LOA_MARK = "loa-banner"
LOA_HTML = """
<div class="loa-banner" style="margin:18px 0 6px;padding:14px 18px;border:1px solid var(--gold,#D9A441);border-radius:12px;background:var(--panel,rgba(217,164,65,.07));line-height:1.65">
  <div style="font-weight:800;color:var(--gold,#D9A441);letter-spacing:.02em">📜 계약 체결 — LOA 양사 서명 완료 (2026.10)</div>
  <div style="font-size:13px;opacity:.85;margin-top:4px">Letter of Approval — preliminary agreements on the potential licensing of &ldquo;The Little Prince&rdquo; IP for SUPERSTORY immersive playtoon experience</div>
</div>
"""

VERCEL_JSON = {
    "redirects": [
        {"source": "/" + old, "destination": "/" + new, "permanent": False}
        for old, new in RENAMES.items()
    ]
}

MISSING_CHECK = [
    "어린왕자_IA_스켈레톤_v0.4.html",
    "forced_alignment_report.html",
    "어린왕자_일정_개발범위_v0.2.xlsx",
]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)
    if not os.path.exists("index.html"):
        sys.exit("❌ index.html이 없습니다. 배포 폴더 루트에서 실행하세요.")

    # 1) 메뉴 파일명 치환
    for path in glob.glob("*.html"):
        with io.open(path, encoding="utf-8") as f:
            src = f.read()
        out, hits = src, 0
        for old, new in RENAMES.items():
            if old in out:
                hits += out.count(old)
                out = out.replace(old, new)
        if hits:
            with io.open(path, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"✅ {path}: 구버전 링크 {hits}건 교체")

    # 2) index.html LOA 배너 (멱등)
    with io.open("index.html", encoding="utf-8") as f:
        idx = f.read()
    if LOA_MARK in idx:
        print("ℹ️  index.html: LOA 배너 이미 있음 — 건너뜀")
    else:
        anchor = '<section id="dash">'
        if anchor in idx:
            idx = idx.replace(anchor, LOA_HTML + "\n" + anchor, 1)
            with io.open("index.html", "w", encoding="utf-8") as f:
                f.write(idx)
            print("✅ index.html: LOA 계약 체결 배너 삽입")
        else:
            print("⚠️  index.html: 삽입 지점(<section id=\"dash\">)을 못 찾음 — 배너 수동 삽입 필요")

    # 3) vercel.json
    with io.open("vercel.json", "w", encoding="utf-8") as f:
        json.dump(VERCEL_JSON, f, ensure_ascii=False, indent=2)
    print("✅ vercel.json 생성 (구주소 리다이렉트 5건)")

    # 4) 누락 파일 점검
    for m in MISSING_CHECK:
        print(("✅ 있음  " if os.path.exists(m) else "⚠️  없음 — 폴더에 넣어야 링크가 살아납니다: ") + m)

    print("\n완료. 이 폴더를 통째로 Vercel에 드래그해서 재배포하세요.")

if __name__ == "__main__":
    main()
