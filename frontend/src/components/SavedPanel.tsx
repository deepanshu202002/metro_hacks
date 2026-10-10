"use client";

import { useState } from "react";
import { Star, Home, Briefcase, MapPin, Leaf, MessageSquare, ThumbsUp, Users, CheckCircle2 } from "lucide-react";

export default function SavedPanel({ onQuickSelectRoute }) {
  const [crowdStation, setCrowdStation] = useState("old_high_court");
  const [crowdReportStatus, setCrowdReportStatus] = useState<string | null>(null);

  const savedPlaces = [
    { id: "home", name: "Home", station: "Vastral Gam", icon: Home, color: "text-blue-500" },
    { id: "work", name: "Office / Work", station: "GIFT City", icon: Briefcase, color: "text-purple-500" },
    { id: "cricket", name: "Stadium Match Hub", station: "Motera Stadium", icon: MapPin, color: "text-rose-500" },
    { id: "uni", name: "University Campus", station: "Gujarat University", icon: Star, color: "text-amber-500" }
  ];

  const handleCrowdReport = async (sentiment) => {
    try {
      const res = await fetch("http://localhost:8000/api/crowd/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          station_id: crowdStation,
          report: sentiment
        })
      });
      const data = await res.json();
      setCrowdReportStatus(`Report recorded: Station marked as '${sentiment}'. Thank you!`);
      setTimeout(() => setCrowdReportStatus(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="h-full flex flex-col p-4 md:p-6 space-y-5 overflow-y-auto pb-20">
      {/* Green Miles Tracker */}
      <div className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/25 p-4 rounded-2xl shadow-xs space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-extrabold text-sm">
            <Leaf size={18} />
            <span>Green Miles Personal Carbon Tracker</span>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">
            Eco Champion
          </span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-black text-foreground tabular-nums">14.8</span>
          <span className="text-xs font-bold text-foreground-muted">kg CO₂ saved vs Cabs</span>
        </div>
        <p className="text-[11px] text-foreground-muted">
          By choosing Metro over private cabs across 18 trips, you prevented ~14,800g of direct carbon emissions!
        </p>
      </div>

      {/* Saved Places */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
          <Star size={16} className="text-primary" />
          <span>Saved Places & Commute Shortcuts</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {savedPlaces.map((place) => {
            const Icon = place.icon;
            return (
              <div
                key={place.id}
                onClick={() => onQuickSelectRoute && onQuickSelectRoute(place.station)}
                className="p-3.5 bg-surface border border-border rounded-xl hover:border-primary/40 hover:bg-surface-hover transition-all cursor-pointer shadow-2xs flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-surface-hover ${place.color}`}>
                    <Icon size={18} />
                  </div>
                  <div>
                    <div className="font-bold text-xs text-foreground">{place.name}</div>
                    <div className="text-[11px] text-foreground-muted">{place.station}</div>
                  </div>
                </div>
                <span className="text-[10px] font-bold text-primary hover:underline">
                  Plan →
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Community Crowd Reporting */}
      <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
            <Users size={16} className="text-primary" />
            <span>Community Crowd Reporting (Live Demo)</span>
          </h3>
          <span className="text-[10px] bg-primary/10 text-primary font-bold px-2 py-0.5 rounded">
            Live Feed
          </span>
        </div>
        <p className="text-xs text-foreground-muted">
          At a platform right now? Share real-time crowd conditions to help fellow commuters:
        </p>

        {/* Station picker */}
        <select
          value={crowdStation}
          onChange={(e) => setCrowdStation(e.target.value)}
          className="w-full bg-surface-hover border border-border rounded-xl p-2.5 text-xs text-foreground font-semibold focus:outline-none"
        >
          <option value="old_high_court">Old High Court (Interchange)</option>
          <option value="motera_stadium">Motera Stadium (Interchange)</option>
          <option value="gnlu">GNLU (Gandhinagar / GIFT Interchange)</option>
          <option value="gift_city">GIFT City</option>
          <option value="apmc">APMC Terminal</option>
          <option value="kalupur">Kalupur Railway Station</option>
        </select>

        {/* 3 Sentiment Buttons */}
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => handleCrowdReport("empty")}
            className="py-2.5 px-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 font-extrabold text-xs transition-all cursor-pointer"
          >
            🟢 Empty / Light
          </button>
          <button
            onClick={() => handleCrowdReport("ok")}
            className="py-2.5 px-3 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 text-amber-700 dark:text-amber-400 font-extrabold text-xs transition-all cursor-pointer"
          >
            🟡 Moderate / OK
          </button>
          <button
            onClick={() => handleCrowdReport("crowded")}
            className="py-2.5 px-3 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-700 dark:text-rose-400 font-extrabold text-xs transition-all cursor-pointer"
          >
            🔴 Very Crowded
          </button>
        </div>

        {crowdReportStatus && (
          <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-xs font-semibold flex items-center gap-1.5 animate-in fade-in">
            <CheckCircle2 size={14} />
            <span>{crowdReportStatus}</span>
          </div>
        )}
      </div>
    </div>
  );
}
