# SUZAKU 静的サイト — ビルド/検証タスク
# 使い方: make build / make verify / make audit / make serve / make clean
.DEFAULT_GOAL := verify
PY ?= python3
PORT ?= 8930

.PHONY: build validate links selftest verify audit serve clean

build:            ## データ検証 + 全ページ生成
	$(PY) scripts/gen.py

validate:         ## データ単一ソースの不変条件を検査
	$(PY) scripts/validate.py

links:            ## リンク切れ検査(生成物対象)
	$(PY) scripts/check_links.py

selftest:         ## 生成→検証→リンク→整合をワンコマンドで
	$(PY) scripts/selftest.py

verify: selftest  ## 既定タスク: フル品質ゲート

audit: build      ## Playwright 監査(要 Node)。AUDIT_WIDTH で幅指定
	@$(PY) -c "from http.server import ThreadingHTTPServer as S, SimpleHTTPRequestHandler as H; import threading,time; s=S(('',$(PORT)),H); threading.Thread(target=s.serve_forever,daemon=True).start(); time.sleep(1); print('serving $(PORT)')" &
	node scripts/audit.js
	AUDIT_WIDTH=1440 node scripts/audit.js

serve: build      ## ローカル配信(マルチスレッド)
	$(PY) -c "from http.server import ThreadingHTTPServer as S, SimpleHTTPRequestHandler as H; S(('',$(PORT)),H).serve_forever()"

clean:            ## 生成の中間物を掃除
	rm -rf .build __pycache__ scripts/__pycache__
