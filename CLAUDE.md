# KawaAni

視聴済みアニメと自分の評価をもとに、次に見るべき3選を提示するダッシュボード。

## 構成
- `frontend/` — Next.js。
- `backend/` — FastAPI + SQLite。uvで環境管理

## コマンド
- backend: `cd backend && uv run uvicorn main:app --reload`
- frontend: `cd frontend && npm run dev`

## ルール
- CSS等の修正は基本的に最小限。レイアウトの作り込みは本質ではないため。
- 基本的に設計判断が入る回答には、必ず公式ドキュメントのURLを添付する。