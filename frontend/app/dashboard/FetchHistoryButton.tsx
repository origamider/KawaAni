"use client"; // ブラウザ側の処理に明示的に変更

import { useState } from "react";

const EXTENSION_ID = process.env.NEXT_PUBLIC_EXTENSION_ID;

export default function FetchHistoryButton() {
  const [titles, setTitles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);// 取得中を表す状態
  const [hasChecked, setHasChecked] = useState(false);

  async function handleClick() {
    setIsLoading(true);
    try {
      const response = await chrome.runtime.sendMessage(EXTENSION_ID, "fetchHistory");
      setTitles(response.titles);
      setHasChecked(true);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <button
        onClick={handleClick}
        disabled={isLoading}
        className="self-start rounded-md bg-accent px-5 py-2 text-sm font-bold text-white transition-colors duration-150 hover:bg-[#f6121d] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-60"
      >
        {isLoading ? "確認中…" : "履歴をチェック"}
      </button>

      {/* 件数が増えたらこの領域だけが縦にスクロールする */}
      <div className="scroll-area max-h-72 min-h-0 flex-1 overflow-y-auto md:max-h-none">
        {titles.length > 0 ? (
          <ul className="flex flex-col gap-2 pr-1">
            {titles.map((title) => (
              <li
                key={title}
                className="rounded-lg bg-white/[0.04] px-4 py-2.5 text-sm text-text"
              >
                {title}
              </li>
            ))}
          </ul>
        ) : (
          <p className="m-0 text-sm text-text-soft text-pretty">
            {hasChecked
              ? "今日はまだ視聴記録が見つかりませんでした。アニメを見たあとに、もう一度チェックしてください。"
              : "「履歴をチェック」を押すと、24時間以内に見たアニメを表示します。"}
          </p>
        )}
      </div>

      <a
        href="https://annict.com/"
        target="_blank"
        rel="noopener noreferrer"
        className="shrink-0 border-t border-line pt-4 text-sm font-medium text-accent transition-colors duration-150 hover:text-[#f6121d] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        Annictで記録する →
      </a>
    </div>
  );
}
