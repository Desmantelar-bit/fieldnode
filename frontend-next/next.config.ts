import type { NextConfig } from "next";

const API_BACKEND = process.env.FIELDNODE_SERVER_API_URL ?? "http://127.0.0.1:8000/api";

const nextConfig: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
  // O Django usa APPEND_SLASH; sem isto, /api/foo/ e /api/foo entram em loop no dev proxy.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_BACKEND}/:path*/`,
      },
    ];
  },
  headers() {
    return Promise.resolve([
      {
        source: "/manifest.json",
        headers: [
          {
            key: "Content-Type",
            value: "application/manifest+json; charset=utf-8",
          },
          {
            key: "Cache-Control",
            value: "public, max-age=86400",
          },
        ],
      },
      {
        source: "/sw.js",
        headers: [
          {
            key: "Content-Type",
            value: "application/javascript; charset=utf-8",
          },
          {
            key: "Cache-Control",
            value: "no-cache, no-store, must-revalidate",
          },
        ],
      },
    ]);
  },
};

export default nextConfig;
