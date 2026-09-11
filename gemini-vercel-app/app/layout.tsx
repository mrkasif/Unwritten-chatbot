import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Unwritten",
  description: "Unwritten — AI chat powered by Google Gemini",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}