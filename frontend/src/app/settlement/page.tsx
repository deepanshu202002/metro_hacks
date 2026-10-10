"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, PieChart, Landmark } from "lucide-react";

export default function SettlementPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/settlement")
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch((e) => console.error(e));
  }, []);

  if (!data) return <div className="p-8 text-foreground">Loading settlement...</div>;

  if (data.error) return <div className="p-8 text-rose-500">{data.error}</div>;

  return (
    <div className="min-h-screen bg-background text-foreground p-4 md:p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 bg-surface hover:bg-surface-hover rounded-full">
            <ArrowLeft size={20} />
          </Link>
          <h1 className="text-2xl font-bold">PPP Settlement & Clearing</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 border border-border bg-surface rounded-2xl">
            <h3 className="text-sm font-semibold text-foreground-muted uppercase tracking-wider">Simulated Trips</h3>
            <div className="text-3xl font-black mt-2 tabular-nums">{data.trips_processed}</div>
          </div>
          <div className="p-5 border border-emerald-500/20 bg-emerald-500/10 rounded-2xl text-emerald-700 dark:text-emerald-400">
            <h3 className="text-sm font-semibold uppercase tracking-wider">Integrated Revenue</h3>
            <div className="text-3xl font-black mt-2 tabular-nums">₹{data.total_integrated_revenue}</div>
          </div>
          <div className="p-5 border border-primary/20 bg-primary/10 rounded-2xl text-primary">
            <h3 className="text-sm font-semibold uppercase tracking-wider">Clearing Fee ({data.clearing_fee_percent}%)</h3>
            <div className="text-3xl font-black mt-2 tabular-nums">₹{data.clearing_entity_revenue}</div>
          </div>
        </div>

        <div className="border border-border bg-surface rounded-2xl overflow-hidden mt-6">
          <div className="bg-surface-hover px-5 py-4 border-b border-border flex justify-between items-center">
            <h2 className="text-lg font-bold flex items-center gap-2"><PieChart size={20}/> Operator Net Pool</h2>
          </div>
          <div className="p-0">
            <table className="w-full text-left">
              <thead className="bg-surface-hover/50 text-xs text-foreground-muted border-b border-border">
                <tr>
                  <th className="px-5 py-3 font-semibold">Operator</th>
                  <th className="px-5 py-3 font-semibold text-right">Legs Served</th>
                  <th className="px-5 py-3 font-semibold text-right">Settled Share (₹)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {Object.entries(data.operator_pools).map(([op, stats]: [string, any]) => (
                  <tr key={op} className="hover:bg-surface-hover/50 transition-colors">
                    <td className="px-5 py-3 font-bold">{op}</td>
                    <td className="px-5 py-3 tabular-nums text-right text-foreground-muted">{stats.legs_served}</td>
                    <td className="px-5 py-3 tabular-nums text-right font-bold text-primary">₹{stats.revenue_share}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="p-5 bg-surface-hover border border-border rounded-xl text-sm text-foreground-muted">
          <h3 className="font-bold text-foreground mb-2 flex items-center gap-2"><Landmark size={16}/> Settlement Rules</h3>
          <ul className="list-disc pl-5 space-y-1">
            <li>A single QR ticket is generated for the combined fare.</li>
            <li>A clearing entity (SPV) takes a {data.clearing_fee_percent}% clearing fee off the top.</li>
            <li>The net pool is divided among operators based on distance, transfers, or pro-rata logic.</li>
            <li>Operators no longer run their own separate AFCs for inter-agency transfers.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
