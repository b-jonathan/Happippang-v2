// app/layout.tsx
"use client";
import React from "react";
import { AuthProvider } from "../context/AuthContext";
import "./globals.css"; // 👈 MAKE SURE THIS IS AT THE TOP

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
