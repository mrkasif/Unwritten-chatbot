/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV === "development";

const nextConfig = {
  rewrites: async () => [
    {
      source: "/api/:path*",
      destination: isDev
        ? "http://127.0.0.1:8000/api/:path*"
        : "/api/",
    },
  ],
};

export default nextConfig;