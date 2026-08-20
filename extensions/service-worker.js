// jsは動的型付き言語なので、型をわざわざ定義しなくてOK。
async function FetchTodayAnimeTitles() {
  //押した瞬間から前
  const items = await chrome.history.search({ text: "", maxResults: 1000});
  // それぞれの要素について、取得したURLがtarget_hostsを部分文字列として持つか判定
  function isTargetURL(url){
    const {hostname, pathname, searchParams } = new URL(url);
    if(hostname === "animestore.docomo.ne.jp" && searchParams.has("workId")) return true;
    if(hostname === "www.amazon.co.jp" && pathname.startsWith("/gp/video/detail")) return true;
    return false;
  };
  const filteredItems = items.filter((item) => {
    return isTargetURL(item.url);
  });
  const candidate_anime = [];
  for(let it of filteredItems){
    candidate_anime.push(it.title);
  }
  //重複除外のため、Setを使うよ。
  const result = Array.from(new Set(candidate_anime));// https://qiita.com/kotakin_dev/items/a19a5a2359144e3ecf1c
  return result;
};


function handleMessages(message, sender, sendResponse) {
  if (message === 'fetchHistory'){
    FetchTodayAnimeTitles().then((titles) => {//.then()はPromise特有。
      sendResponse({titles});// フロント側に流す
    });
    return true;
  }
}
// AsyncはPromise型で返されるらしい。
// メッセージ受け口実装。(参考:https://developer.chrome.com/docs/extensions/develop/concepts/messaging?hl=ja)
chrome.runtime.onMessageExternal.addListener(handleMessages);
