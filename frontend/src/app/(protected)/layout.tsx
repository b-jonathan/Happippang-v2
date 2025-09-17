// app/(protected)/layout.tsx
"use client";

import React, { useEffect, useState } from "react";
// import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth(); // throws if outside provider
  // const router = useRouter();
  const [hydrated, setHydrated] = useState(false);

  // Avoid hydration mismatch
  useEffect(() => {
    setHydrated(true);
  }, []);

  // Redirect if not logged in
  // useEffect(() => {
  //   if (hydrated && !loading && !user) {
  //     router.replace("/login");
  //   }
  // }, [hydrated, loading, user, router]);

  if (!hydrated || loading || !user) return <div>Loading...</div>;

  return <>{children}</>;
}
