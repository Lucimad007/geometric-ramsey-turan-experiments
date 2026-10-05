"use client";

import dynamic from "next/dynamic";

const Explorer = dynamic(() => import("@/components/Explorer"), {
  ssr: false,
  loading: () => <p className="loading">Loading viewer…</p>,
});

export default function Page() {
  return <Explorer />;
}
