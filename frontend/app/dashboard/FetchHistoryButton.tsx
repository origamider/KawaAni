"use client";

import { useState } from "react";
import Modal from "@/components/Modal";

const EXTENSION_ID = process.env.NEXT_PUBLIC_EXTENSION_ID;
const BACKEND_URL = "http://127.0.0.1:8000";

// anilist.pyのsearch_animeの返り値に合わせる。
type AnilistMedia = {
  id: number;
  idMal: number;
  title: { romaji: string; english: string | null; native: string };
  coverImage: { medium: string };
};

// main.pyのanilist_searchに合わせる。
type SearchResult = {
  cleaned_title: string;
  anime: AnilistMedia | null;
};

export default function FetchHistoryButton() {
  const [titles, setTitles] = useState<string[]>([]);// 視聴履歴の文字列配列
  const [isLoading, setIsLoading] = useState(false);// ローディング中の表示を制御するため
  const [hasChecked, setHasChecked] = useState(false);

  // モーダル用の状態
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [score, setScore] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

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

  async function openAnilistModal(title: string) {
    setSelectedTitle(title);
    setSearchResult(null);
    setSaveMessage(null);
    setIsSearching(true);
    try {
      const res = await fetch(
        `${BACKEND_URL}/anilist/search?title=${encodeURIComponent(title)}`
      );
      const data: SearchResult = await res.json();
      setSearchResult(data);
    } finally {
      setIsSearching(false);
    }
  }

  function closeModal() {
    setSelectedTitle(null);
    setSearchResult(null);
    setSaveMessage(null);
  }

  async function handleSaveScore() {
    if (!searchResult?.anime) return;
    setIsSaving(true);
    try {
      const res = await fetch(`${BACKEND_URL}/anilist/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mediaId: searchResult.anime.id, score }),
      });
      const data: { ok: boolean; error?: string } = await res.json();
      if (data.ok) {
        setSaveMessage("AniListに記録しました");
      } else {
        setSaveMessage(data.error ?? "記録に失敗しました");
      }
    } finally {
      setIsSaving(false);
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

      <div className="scroll-area max-h-72 min-h-0 flex-1 overflow-y-auto md:max-h-none">
        {titles.length > 0 ? (
          <ul className="flex flex-col gap-2 pr-1">
            {titles.map((title) => (
              <li key={title}>
                <button
                  onClick={() => openAnilistModal(title)}
                  className="w-full rounded-lg bg-white/[0.04] px-4 py-2.5 text-left text-sm text-text transition-colors duration-150 hover:bg-white/[0.08]"
                >
                  {title}
                </button>
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
      
      <Modal isOpen={selectedTitle !== null} onClose={closeModal}>
        <div className="flex items-center gap-3 pr-8">
          <span className="h-5 w-1 shrink-0 rounded-full bg-accent" aria-hidden="true" />
          <h2 className="m-0 font-display text-lg text-text text-balance">
            AniListに記録
          </h2>
        </div>

        <div className="mt-5">
          {isSearching && (
            <p className="py-10 text-center text-sm text-text-soft">検索中…</p>
          )}

          {!isSearching && searchResult?.anime && (
            <div className="flex flex-col gap-5">
              <div className="flex gap-4">
                <div className="relative aspect-3/4 w-28 shrink-0 overflow-hidden rounded-lg border border-line">
                  <img
                    src={searchResult.anime.coverImage.medium}
                    alt={searchResult.anime.title.native}
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="flex min-w-0 flex-col gap-1 pt-1">
                  <p className="m-0 line-clamp-3 text-base font-bold text-text text-balance">
                    {searchResult.anime.title.native}
                  </p>
                  {searchResult.anime.title.english && (
                    <p className="m-0 line-clamp-2 text-xs text-text-soft">
                      {searchResult.anime.title.english}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-2 border-t border-line pt-4">
                <label htmlFor="score" className="text-xs font-medium text-text-soft">
                  スコア(10点満点)
                </label>
                <input
                  id="score"
                  type="number"
                  min={1}
                  max={10}
                  value={score}
                  onChange={(e) => setScore(Number(e.target.value))}
                  className="w-20 rounded-md border border-line bg-transparent px-3 py-2 text-lg font-bold text-text"
                />
              </div>

              <button
                onClick={handleSaveScore}
                disabled={isSaving}
                className="rounded-md bg-accent px-4 py-2.5 text-sm font-bold text-white transition-colors duration-150 hover:bg-[#f6121d] disabled:opacity-60"
              >
                {isSaving ? "記録中…" : "AniListに記録する"}
              </button>

              {saveMessage && (
                <p className="m-0 text-xs text-text-soft">{saveMessage}</p>
              )}
            </div>
          )}

          {!isSearching && searchResult && !searchResult.anime && (
            <p className="py-10 text-center text-sm text-text-soft text-pretty">
              「{searchResult.cleaned_title}」に一致するアニメが見つかりませんでした。
            </p>
          )}
        </div>
      </Modal>
    </div>
  );
}
