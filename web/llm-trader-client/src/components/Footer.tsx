"use client";

import Image from "next/image";

export default function Footer() {
  return (
    <footer className="relative w-full border-t border-[#1e293b] bg-[#0b0d12] text-perspectiv-muted text-sm mt-12 py-8 px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Image
          src="/assets/perspectiv_logo_no_letters.PNG"
          alt="Perspectiv Cube"
          width={22}
          height={22}
          className="opacity-75"
        />
        <span className="text-perspectiv-text text-[13px] tracking-wide">
          © 2025 Perspectiv — All Rights Reserved
        </span>
      </div>

      <div className="flex items-center gap-4 text-xs pt-[1px]">
        <a
          href="https://github.com/nicolasroy11"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-perspectiv-accent transition"
        >
          GitHub
        </a>
        <a
          href="mailto:contact@perspectiv.ai"
          className="hover:text-perspectiv-accent transition"
        >
          Contact
        </a>
      </div>
    </footer>
  );
}
