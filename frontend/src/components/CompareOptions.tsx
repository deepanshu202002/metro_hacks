"use client";

import { useState } from "react";
import { Train, Bus, Car, Leaf, ArrowRight, ChevronDown, ChevronUp, CheckCircle2, ShieldCheck, Clock, Ticket } from "lucide-react";

const LINE_BADGE_COLORS = {
  Blue: "bg-[#1D6FD8] text-white",
  Red: "bg-[#D7263D] text-white",
  Yellow: "bg-[#F2B705] text-slate-900",
  Violet: "bg-[#7C3AED] text-white",
  BRTS: "bg-[#0EA5E9] text-white",
  Direct: "bg-[#7C3AED] text-white",
  "GNLU-GIFT Connector": "bg-[#0EA5E9] text-white",
  "GIFT SEZ Free Shuttle": "bg-[#10B981] text-white",
  walk: "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200",
  cab: "bg-[#F97316] text-white"
};

export default function CompareOptions({ data, selectedOption, onSelect, onOpenTicketModal }) {
  const [expandedCard, setExpandedCard] = useState(null);
  const [fareSplits, setFareSplits] = useState<any>({});

  if (!data || !data.options) {
    return (
      <div className="p-6 text-center text-foreground-muted">
        No routes available.
      </div>
    );
  }

  const options = data.options;
  const cards = [];

  // 1. Primary Metro Option
  if (options.metro_only) {
    const m = options.metro_only;
    const isDirect = m.is_direct || m.transfers === 0;
    cards.push({
      id: "metro_only",
      title: isDirect ? "Direct Metro Train" : "Metro with Transfer",
      mode: "metro",
      icon: Train,
      badge: m.badge || (isDirect ? "Direct • No Transfers" : "Recommended"),
      time_min: m.total_time_min,
      fare: m.fare,
      smart_card_fare: m.smart_card_fare || Math.max(5, m.fare - 2),
      distance_km: m.distance_km,
      transfers: m.transfers || 0,
      co2_saved: m.co2_saved_grams || 180,
      legs: m.legs || [],
      reliability: 98.6
    });
  }

  // 2. Feeder Bus Option (GNLU <-> GIFT City)
  if (options.feeder_bus) {
    const b = options.feeder_bus;
    cards.push({
      id: "feeder_bus",
      title: "Metro + Feeder Bus",
      mode: "bus",
      icon: Bus,
      badge: "Every 30m Feeder",
      time_min: b.total_time_min,
      fare: b.fare,
      smart_card_fare: b.smart_card_fare || b.fare,
      distance_km: b.distance_km,
      transfers: b.transfers || 1,
      co2_saved: b.co2_saved_grams || 140,
      legs: b.legs || [],
      reliability: 94.2
    });
  }

  // 3. Free Shuttle Option
  if (options.shuttle) {
    const s = options.shuttle;
    cards.push({
      id: "shuttle",
      title: "Free GIFT Shuttle + Metro",
      mode: "shuttle",
      icon: Train,
      badge: "₹0 Shuttle Connector",
      time_min: s.total_time_min,
      fare: s.fare,
      smart_card_fare: s.smart_card_fare || s.fare,
      distance_km: s.distance_km,
      transfers: s.transfers || 1,
      co2_saved: s.co2_saved_grams || 160,
      legs: s.legs || [],
      reliability: 97.5
    });
  }

  // 4. Cab Option
  if (options.cab) {
    const c = options.cab;
    cards.push({
      id: "cab",
      title: "Taxi / Cab Ride",
      mode: "cab",
      icon: Car,
      badge: c.badge || "Door-to-Door",
      time_min: c.total_time_min,
      fare: c.fare,
      smart_card_fare: c.fare,
      distance_km: c.distance_km,
      transfers: 0,
      co2_saved: 0,
      legs: c.legs || [],
      reliability: 88.0
    });
  }

  const toggleExpand = async (id, e) => {
    e.stopPropagation();
    if (expandedCard === id) {
      setExpandedCard(null);
      return;
    }
    setExpandedCard(id);
    
    // Fetch fare split if not already fetched
    const card = cards.find(c => c.id === id);
    if (card && card.legs.length > 0 && !fareSplits[id]) {
      try {
        const res = await fetch("http://localhost:8000/api/fare/split", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            legs: card.legs,
            integrated_fare: card.smart_card_fare,
            method: "pro-rata"
          })
        });
        if (res.ok) {
          const splitData = await res.json();
          setFareSplits(prev => ({ ...prev, [id]: splitData.splits }));
        }
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="space-y-3 pb-8">
      {data.fallback_message && (
        <div className="p-3 bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-400 rounded-xl text-xs font-semibold">
          {data.fallback_message}
        </div>
      )}

      {cards.map((c) => {
        const Icon = c.icon;
        const isSelected = selectedOption === c.id;
        const isExpanded = expandedCard === c.id;

        return (
          <div
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={`border rounded-2xl p-4 transition-all cursor-pointer relative shadow-xs ${
              isSelected
                ? "bg-surface border-primary ring-2 ring-primary/20 shadow-md"
                : "bg-surface/80 hover:bg-surface border-border hover:border-border/80"
            }`}
          >
            {/* Header: Title, Badge, Time, Fare */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold ${
                  isSelected ? "bg-primary text-white" : "bg-surface-hover text-foreground-muted"
                }`}>
                  <Icon size={20} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-foreground text-sm md:text-base">
                      {c.title}
                    </h3>
                  </div>
                  <span className="inline-block mt-0.5 px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wide bg-primary/10 text-primary">
                    {c.badge}
                  </span>
                </div>
              </div>

              {/* Time & Fare */}
              <div className="text-right">
                <div className="text-xl md:text-2xl font-black text-foreground tabular-nums tracking-tight">
                  {c.time_min} <span className="text-xs font-bold text-foreground-muted">min</span>
                </div>
                <div className="text-xs font-bold text-foreground flex items-center justify-end gap-1.5 mt-0.5">
                  <span className="text-emerald-600 dark:text-emerald-400 font-extrabold">₹{c.smart_card_fare}</span>
                  {c.smart_card_fare < c.fare && (
                    <span className="text-[10px] text-foreground-muted line-through font-normal">₹{c.fare}</span>
                  )}
                  {c.smart_card_fare < c.fare && (
                    <span className="text-[9px] bg-emerald-500/10 text-emerald-600 px-1 rounded font-bold">Card</span>
                  )}
                </div>
              </div>
            </div>

            {/* Integrated Fare Banner */}
            {c.smart_card_fare < c.fare && (
              <div className="mt-3 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg text-emerald-700 dark:text-emerald-400 text-xs font-semibold">
                Integrated fare: Pay ONCE ₹{c.smart_card_fare} vs ₹{c.fare} if bought separately, you save ₹{c.fare - c.smart_card_fare}.
              </div>
            )}

            {/* Metrics: Distance, Transfers, CO2 Saved */}
            <div className="flex items-center justify-between text-xs text-foreground-muted border-t border-border/60 pt-3 mt-3">
              <div className="flex items-center gap-2 font-medium">
                <span>{c.distance_km} km</span>
                <span>•</span>
                <span>{c.transfers === 0 ? "Direct" : `${c.transfers} transfer`}</span>
                {c.co2_saved > 0 && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-bold">
                      <Leaf size={11} /> {c.co2_saved}g CO₂ saved
                    </span>
                  </>
                )}
              </div>

              <button
                type="button"
                onClick={(e) => toggleExpand(c.id, e)}
                className="text-xs font-bold text-primary hover:underline flex items-center gap-0.5 cursor-pointer"
              >
                <span>{isExpanded ? "Hide legs" : "Timeline"}</span>
                {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>

            {/* Expandable Route Timeline */}
            {isExpanded && (
              <div className="mt-3 pt-3 border-t border-border/60 space-y-2.5 animate-in fade-in duration-300">
                {c.legs.map((leg, lIdx) => {
                  const badgeClass = (LINE_BADGE_COLORS as any)[leg.line] || "bg-slate-600 text-white";
                  return (
                    <div key={lIdx} className="flex items-start gap-2.5 text-xs">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                      <div className="flex-1">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${badgeClass}`}>
                            {leg.line || leg.mode}
                          </span>
                          <span className="font-semibold text-foreground">
                            {leg.from} → {leg.to}
                          </span>
                          <span className="text-[10px] text-foreground-muted tabular-nums ml-auto">
                            {leg.depart} - {leg.arrive}
                          </span>
                        </div>
                        {leg.dist && (
                          <div className="text-[10px] text-foreground-muted mt-0.5">
                            {leg.dist} km • ₹{leg.fare || 0}
                          </div>
                        )}
                        {/* Transfer Walk Info */}
                        {lIdx < c.legs.length - 1 && c.legs[lIdx+1].mode !== "walk" && leg.mode !== "walk" && (
                          <div className="mt-1 ml-4 pl-3 border-l-2 border-dashed border-border py-1 text-[10px] text-foreground-muted font-medium flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600" />
                            Transfer: ~3 mins walking distance
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {/* Fare Split Panel */}
                {fareSplits[c.id] && fareSplits[c.id].length > 1 && (
                  <div className="mt-3 bg-surface border border-border rounded-xl overflow-hidden">
                    <div className="bg-surface-hover px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider border-b border-border">
                      Operator Settlement (PPP)
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left">
                        <thead className="bg-surface-hover/50 text-foreground-muted border-b border-border/50">
                          <tr>
                            <th className="px-3 py-1.5 font-medium">Operator</th>
                            <th className="px-3 py-1.5 font-medium">Legs</th>
                            <th className="px-3 py-1.5 font-medium">Leg Fare</th>
                            <th className="px-3 py-1.5 font-medium">Share</th>
                            <th className="px-3 py-1.5 font-medium">Net vs Standalone</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/50">
                          {fareSplits[c.id].map((op, i) => (
                            <tr key={i} className="hover:bg-surface-hover transition-colors">
                              <td className="px-3 py-1.5 font-semibold text-foreground">{op.operator}</td>
                              <td className="px-3 py-1.5">{op.legs}</td>
                              <td className="px-3 py-1.5">₹{op.leg_fare}</td>
                              <td className="px-3 py-1.5 font-bold text-primary">₹{op.share}</td>
                              <td className={`px-3 py-1.5 font-medium ${op.net_vs_standalone < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                {op.net_vs_standalone > 0 ? '+' : ''}{op.net_vs_standalone}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Ticket Action Button */}
                <div className="pt-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onOpenTicketModal && onOpenTicketModal(c);
                    }}
                    className="w-full py-2 px-3 rounded-lg bg-surface-hover hover:bg-border text-foreground font-bold text-xs flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <Ticket size={14} className="text-primary" />
                    <span>Generate QR Token (₹{c.smart_card_fare})</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
