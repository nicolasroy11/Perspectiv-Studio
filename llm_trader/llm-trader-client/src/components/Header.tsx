"use client";

import Image from "next/image";
import Link from "next/link";

export default function Header() {
  return (
    <header className="flex items-center gap-3 bg-gray-950 border-b border-gray-800 px-4 py-3">
      <Link href="/" className="flex items-center gap-2">
        <Image
          src="/assets/perspectiv_logo_no_letters.png"
          alt="Perspectiv Logo"
          width={36}
          height={36}
          priority
        />
        <h1 className="text-xl font-semibold text-blue-400 tracking-wide">
          Perspectiv LLM Trader
        </h1>
      </Link>
    </header>
  );
}
