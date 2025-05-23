/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://gastroapi.rohitkphilip.com/api/:path*',
      },
    ];
  },
}

module.exports = nextConfig