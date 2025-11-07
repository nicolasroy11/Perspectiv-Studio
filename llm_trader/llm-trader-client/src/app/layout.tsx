import "./globals.css";
import Providers from "./providers";
import Header from "../components/Header";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Perspectiv LLM Trader Dashboard",
  description: "Interactive trading visualizations and LLM decision analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100">
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  );
}
