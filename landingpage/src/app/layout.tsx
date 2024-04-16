import './globals.css'
import type { Metadata } from 'next'
import {Red_Hat_Display} from "next/font/google";

const inter = Red_Hat_Display({subsets: ["latin"]});

export const metadata: Metadata = {
  title: "The World Calendar | Coming Soon",
  description: "Coming Soon: The World Calendar. Powered by Snazzy Studio. Follow us on Twitter or our blog for latest updates.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
