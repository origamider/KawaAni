import Image from 'next/image'
import FetchHistoryButton from './FetchHistoryButton'

type AnimeData = {
  title_japanese: string
  image_url: string
}

const anilistAuthorizeParams = new URLSearchParams({
  client_id: process.env.NEXT_PUBLIC_ANILIST_CLIENT_ID!,
  redirect_uri: process.env.NEXT_PUBLIC_ANILIST_REDIRECT_URI!,
  response_type: "code",
})
const anilistLoginUrl = `https://anilist.co/api/v2/oauth/authorize?${anilistAuthorizeParams}`

export default async function Page() {
  const [res, statusRes] = await Promise.all([
    fetch("http://127.0.0.1:8000/recommend/next"),
    fetch("http://127.0.0.1:8000/auth/anilist/status"),
  ])
  const top3AnimeList: AnimeData[] = await res.json()
  const { connected }: { connected: boolean } = await statusRes.json()

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 pt-12 pb-16">
      <header className="flex flex-col gap-1.5">
        <h1 className="m-0 font-display text-4xl text-accent">KawaAni</h1>
        <p className="m-0 text-sm text-text-soft text-pretty">
          あなたにマッチしたアニメを提案します
        </p>
        {connected ? (
          <p className="mt-1 text-sm text-text-soft">
            AniList: kawarinとして連携中
          </p>
        ) : (
          <a
            href={anilistLoginUrl}
            className="mt-1 self-start text-sm font-medium text-accent transition-colors duration-150 hover:text-[#f6121d] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            AniListと連携する →
          </a>
        )}
      </header>

      {/* md以上で高さを固定し、両カードを同じ縦幅・横幅に揃える */}
      <div className="grid gap-6 md:h-[560px] md:grid-cols-2">
        <section className="flex min-h-0 flex-col gap-5 rounded-2xl border border-line bg-surface p-6">
          <div className="flex items-center gap-3">
            <span className="h-5 w-1 shrink-0 rounded-full bg-accent" aria-hidden="true" />
            <h2 className="m-0 font-display text-lg text-text text-balance">
              あなたへのおすすめ3選
            </h2>
          </div>

          <div className="grid min-h-0 flex-1 grid-cols-3 content-start gap-3">
            {top3AnimeList.map((anime) => (
              <div key={anime.title_japanese} className="flex flex-col gap-2">
                <div className="relative aspect-[3/4] overflow-hidden rounded-lg border border-line">
                  <Image
                    src={anime.image_url}
                    alt={anime.title_japanese}
                    fill
                    sizes="(max-width: 768px) 30vw, 140px"
                    className="object-cover"
                  />
                </div>
                <p className="m-0 line-clamp-2 text-xs leading-snug font-medium text-text">
                  {anime.title_japanese}
                </p>
              </div>
            ))}
          </div>

          <p className="m-0 text-xs text-text-soft">視聴履歴とスコアから選びました</p>
        </section>

        <section className="flex min-h-0 flex-col gap-5 rounded-2xl border border-line bg-surface p-6">
          <div className="flex items-center gap-3">
            <span className="h-5 w-1 shrink-0 rounded-full bg-accent" aria-hidden="true" />
            <h2 className="m-0 font-display text-lg text-text text-balance">記録忘れチェック</h2>
          </div>

          <FetchHistoryButton />
        </section>
      </div>
    </div>
  )
}
