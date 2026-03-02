import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Bangalore Traffic Intelligence",
  description:
    "Real-time traffic monitoring, congestion heatmap, and incident tracking for Bangalore corridors.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{ background: "#030712", color: "#f3f4f6" }}>{children}</body>
    </html>
  );
}
