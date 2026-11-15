import type { Metadata } from "next";
import { Inter, Space_Grotesk, Snippet, Staatliches } from "next/font/google";
import { ServiceWorkerBridge } from "@/components/ServiceWorkerBridge";
import "./globals.css";
import "./heat-grid.css";

// Display: Space Grotesk (geométrica, neon-friendly) — usada em títulos e KPIs.
const spaceGrotesk = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
  display: "swap",
});

// Marca FieldNode: FIELD usa Snippet (geométrica, com os terminais curvos do
// 'l' e do 'd' que assinam a marca na versão atual). Peso único (400).
const snippet = Snippet({
  variable: "--font-brand-field",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

// Marca FieldNode: NODE usa Staatliches (monumental, ampla, com textura aplicada via CSS).
const staatliches = Staatliches({
  variable: "--font-brand-node",
  subsets: ["latin"],
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FieldNode",
  description: "Dashboard de telemetria agrícola offline-first",
};

// Script inline executado antes do primeiro paint — evita flash de tema errado.
const themeScript = `
(function(){
  try {
    var t = localStorage.getItem('fn-theme');
    if (!t) {
      t = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    document.documentElement.classList.add(t);
  } catch(e) {
    document.documentElement.classList.add('dark');
  }
})();
`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="pt-BR"
      className={`${spaceGrotesk.variable} ${inter.variable} ${snippet.variable} ${staatliches.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        {/* Anti-flash: aplica tema antes do paint */}
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/icon-192.png" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
        <link rel="preconnect" href="https://tile.openstreetmap.org" />
        <link rel="dns-prefetch" href="https://tile.openstreetmap.org" />
      </head>
      <body className="min-h-full flex flex-col" suppressHydrationWarning>
        <ServiceWorkerBridge />
        {children}
      </body>
    </html>
  );
}
