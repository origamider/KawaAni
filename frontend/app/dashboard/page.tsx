import Image from 'next/image'
import FetchHistoryButton from './FetchHistoryButton'

type AnimeData = {
  title_japanese: string
  image_url: string
}

export default async function Page() {
  const res = await fetch("http://127.0.0.1:8000/recommend/next")
  const top3AnimeList: AnimeData[] = await res.json()

  return (
    <div className="max-w-[860px] mx-auto px-5 pt-12 pb-20 flex flex-col gap-10">
      <div className="flex flex-col gap-1.5">
        <h1 className="font-display text-[36px] bg-gradient-to-r from-violet to-magenta bg-clip-text text-transparent drop-shadow-[0_0_18px_rgba(155,107,255,0.45)] m-0">
          KawaAni
        </h1>
        <p className="font-body text-sm text-text-soft m-0">あなたにマッチしたアニメを提案します</p>
      </div>

      <section className="rounded-[28px] p-7 flex flex-col gap-5 bg-white/5 border border-violet/20">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2.5">
            <span className="size-2.5 rounded-full bg-violet shadow-[0_0_10px_2px_rgba(155,107,255,0.7)] shrink-0" />
            <h2 className="font-display text-xl text-text m-0">あなたへのおすすめ3選</h2>
          </div>
          <p className="text-[13px] text-text-soft m-0">視聴履歴とスコアから選びました</p>
        </div>

        <div className="flex gap-6 flex-wrap">
          {top3AnimeList.map((anime) => (
            <div
              key={anime.title_japanese}
              className="w-[200px] bg-surface rounded-3xl p-3 flex flex-col gap-2 border border-violet/25 shadow-[0_0_30px_-10px_rgba(155,107,255,0.4)]"
            >
              <div className="relative rounded-2xl overflow-hidden aspect-[3/4]">
                <Image
                  src={anime.image_url}
                  alt={anime.title_japanese}
                  fill
                  sizes="200px"
                  className="object-cover"
                />
              </div>
              <p className="text-sm font-bold text-text leading-snug line-clamp-2 m-0">
                {anime.title_japanese}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-[28px] p-7 flex flex-col gap-5 bg-white/5 border border-cyan/20">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2.5">
            <span className="size-2.5 rounded-full bg-cyan shadow-[0_0_10px_2px_rgba(69,224,192,0.7)] shrink-0" />
            <h2 className="font-display text-xl text-text m-0">記録忘れチェック</h2>
          </div>
          <p className="text-[13px] text-text-soft m-0">AniListへの記録を忘れていませんか？</p>
        </div>

        <FetchHistoryButton />
      </section>
    </div>
  )
}
