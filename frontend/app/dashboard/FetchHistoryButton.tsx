"use client"; // ブラウザ側の処理に明示的に変更

import { useState } from "react";

const EXTENSION_ID = process.env.NEXT_PUBLIC_EXTENSION_ID;

export default function FetchHistoryButton() {
  const [titles, setTitles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
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
    <>
      <div>
        <button
          onClick={handleClick}
          disabled={isLoading}
          className="font-body font-bold text-sm text-[#0B1F1B] bg-cyan rounded-full px-6 py-2.5 shadow-[0_0_20px_-4px_rgba(69,224,192,0.7)] transition hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-cyan focus-visible:outline-offset-2 disabled:opacity-60 disabled:cursor-default disabled:hover:translate-y-0"
        >
          {isLoading ? "確認中…" : "履歴をチェック"}
        </button>
      </div>

      {hasChecked && titles.length === 0 && (
        <p className="text-[13px] text-text-soft bg-white/5 border border-white/10 rounded-2xl px-5 py-4">
          今日はまだ視聴記録が見つかりませんでした。
        </p>
      )}

      {titles.length > 0 && (
        <ul className="flex flex-col gap-2.5">
          {titles.map((title) => (
            <li
              key={title}
              className="flex items-center gap-2.5 bg-surface rounded-full px-4.5 py-2.5 border border-cyan/20"
            >
              <span className="flex items-center justify-center size-5 rounded-full bg-cyan text-[#0B1F1B] text-xs shrink-0">
                ✓
              </span>
              <span className="text-sm font-medium text-text">{title}</span>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
