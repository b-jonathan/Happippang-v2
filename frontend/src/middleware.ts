// frontend/src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const p = req.nextUrl.pathname;

  // Let API and assets pass through (prevents redirect loops)
  if (p.startsWith("/api") || p.startsWith("/_next") || p === "/favicon.ico") {
    return NextResponse.next();
  }

  // Your page-level auth/redirect logic can go here if desired,
  // but you already guard with (protected)/layout, so likely no-op:
  return NextResponse.next();
}

// Apply to everything; exclusions handled above
export const config = { matcher: ["/:path*"] };
