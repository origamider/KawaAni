import type { NextConfig } from "next";

// 参考資料:https://nextjs.org/docs/app/getting-started/images#remote-images
// remoteからの画像URLを取得するため、こちらで許可リストを作成している。

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'myanimelist.net',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.myanimelist.net',
        pathname: '/images/**',
      },
    ],
  },
};

export default nextConfig;