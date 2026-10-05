import type { Metadata } from "next";
import { Fraunces, Geist } from "next/font/google";
import "./globals.css";
import "./viewer.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const serif = Fraunces({ subsets: ["latin"], variable: "--font-serif" });
const geist = Geist({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  title: "Geometric Ramsey–Turán experiments",
  description:
    "Finite-sample viewer for the complex Bollobás–Erdős edge rules. Not a proof of the Ramsey–Turán densities.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className={`${serif.variable} ${geist.variable}`}>
        <TooltipProvider>{children}</TooltipProvider>
      </body>
    </html>
  );
}
