/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',          // tells Next to emit a static export
  images: { unoptimized: true } // safe for static sites if you use <Image/>
};

module.exports = nextConfig;
