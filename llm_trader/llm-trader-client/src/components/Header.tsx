"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 flex items-center justify-between bg-[#0b0d12] border-b border-[#1e293b] px-8 py-4 shadow-lg">
      <Link href="/" className="flex items-center gap-3 group">
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Image
            src="/assets/perspectiv_logo_no_letters.PNG"
            alt="Perspectiv Logo"
            width={42}
            height={42}
            priority
            className="drop-shadow-md group-hover:scale-105 transition-transform"
          />
        </motion.div>
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-[1.25rem] font-semibold tracking-wider text-[#5bc0ff] group-hover:text-[#7a6fff] transition-colors"
        >
          Perspectiv LLM Trader
        </motion.h1>
      </Link>

      <nav className="flex items-center gap-6 text-sm text-gray-400">
        <Link href="/dashboard" className="hover:text-[#5bc0ff] transition">
          Dashboard
        </Link>
        <Link href="/analytics" className="hover:text-[#5bc0ff] transition">
          Analytics
        </Link>
        <Link href="/about" className="hover:text-[#5bc0ff] transition">
          About
        </Link>
      </nav>
    </header>
  );
}
