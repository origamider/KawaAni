import Image from 'next/image'

type AnimeData = {
  title_japanese: string
  image_url: string
}

export default async function Page() {
  let res = (await fetch("http://127.0.0.1:8000/recommend/next"))
  const top3AnimeList: AnimeData[] = await res.json()
  return (
    <div>
      {top3AnimeList.map((anime) => (
        <div key={anime.title_japanese}>
          <Image
            src={anime.image_url}
            alt={anime.title_japanese}
            width={200}
            height={200}
          />
          <p>{anime.title_japanese}</p>
        </div>
      ))}
    </div>
  )
}
