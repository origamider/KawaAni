export default async function Page() {
  let top3data = await fetch("http://127.0.0.1:8000/recommend/next")
  console.log("top3data = ",top3data)
  let data = await top3data.json()
  console.log("data = ",data)
  return <p>DashBoard Show!</p>
}