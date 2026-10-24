import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Eventra AI — Intelligent Event Planning",
  description:
    "Plan, organize, and manage any event with AI-powered recommendations, smart budgeting, and a complete planning toolkit.",
  keywords: "event planning, AI event planner, wedding planner, birthday planner, hackathon organizer",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
