"use client"; // ブラウザ側の処理に明示的に変更

import { useState } from "react";

const EXTENSION_ID = process.env.NEXT_PUBLIC_EXTENSION_ID;

export default function FetchHistoryButton(){
  const [titles, setTitles] = useState<string[]>([]);// Titlesの部分は更新して欲しい。

  async function handleClick() {// sendMessage参考(https://developer.chrome.com/docs/extensions/reference/api/runtime?hl=ja)
    const response = await chrome.runtime.sendMessage(EXTENSION_ID,"fetchHistory");
    setTitles(response.titles);
  }

  return (
    <section>
      <h2>記録忘れチェック</h2>
      <button onClick={handleClick}>更新</button>
      <ul>
        {titles.map((title) => (
          <li key={title}>{title}</li>
        ))}
      </ul>
    </section>
  );
}