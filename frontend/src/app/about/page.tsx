"use client";

import Link from "next/link";
import { ArrowLeft, Info, Landmark } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background text-foreground p-4 md:p-8 font-sans">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 bg-surface hover:bg-surface-hover rounded-full">
            <ArrowLeft size={20} />
          </Link>
          <h1 className="text-2xl font-bold">About One Journey (PS-08)</h1>
        </div>

        <div className="p-5 border border-border bg-surface rounded-2xl space-y-4 text-sm leading-relaxed">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Info size={18} className="text-primary"/> Assumptions & Constraints
          </h2>
          <p>
            This prototype was built for the <strong>DevFest Gandhinagar Metro Hacks (PS-08 "One City, One Journey")</strong>.
            Due to the constraints of developing on a moving train with patchy internet, the following assumptions were made:
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Offline First:</strong> The app bundles its own JSON timetables and routing logic to function entirely offline.</li>
            <li><strong>Synthetic Data:</strong> Some timetables, operator fares, and integration points (BRTS/AMTS hubs) use synthesized data for demonstration purposes, marked accordingly.</li>
            <li><strong>Local AI:</strong> Voice and text routing logic falls back to a locally hosted Ollama instance when network is down, and determinisic regex when Ollama is unavailable.</li>
            <li><strong>SVG Schematic Map:</strong> When map tiles fail to load, an auto-scaling SVG schematic network diagram is utilized as a fallback map.</li>
          </ul>
        </div>

        <div className="p-5 border border-border bg-surface rounded-2xl space-y-4 text-sm leading-relaxed">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Landmark size={18} className="text-primary"/> PPP Settlement Model
          </h2>
          <p>
            To achieve "One Ticket, One Fare", a Public-Private Partnership (PPP) model is proposed for clearing and settlement:
          </p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Unified Fare:</strong> The user pays a slightly discounted single fare for a journey involving multiple operators (GMRC, BRTS, AMTS).</li>
            <li><strong>Clearing Entity (SPV):</strong> An independent Special Purpose Vehicle handles the settlement and takes a nominal clearing fee (e.g., 1.5%).</li>
            <li><strong>Fare Apportionment:</strong> The remaining revenue pool is automatically distributed among the constituent operators based on a distance-weighted or pro-rata logic.</li>
            <li><strong>View Simulation:</strong> Check the <Link href="/settlement" className="text-primary hover:underline">Settlement Dashboard</Link> to see a simulation of 200 random daily trips cleared using this model.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
