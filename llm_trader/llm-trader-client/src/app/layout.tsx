import "./globals.css";
import Providers from "./providers";
import Header from "../components/Header";
import Footer from "../components/Footer";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Perspectiv LLM Trader Dashboard",
  description: "Interactive trading visualizations and LLM decision analytics",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-perspectiv-dark text-perspectiv-text">
        <Providers>
          <Header />
          <main className="px-8 pt-8 pb-20 max-w-7xl mx-auto">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
