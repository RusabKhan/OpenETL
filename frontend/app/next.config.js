const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.dataomnisolutions.com",
        pathname: "/main/logos/**",
      },
    ],
  },
};

module.exports = nextConfig;
