"use client";

import { useState, useEffect } from "react";
import { Search, MapPin, Navigation, ArrowUpDown, Clock, Mic, MicOff, Accessibility, Sparkles, Building2, Trophy } from "lucide-react";

const QUICK_CHIPS = [
  { label: "Thaltej -> GIFT City", origin: "Thaltej", dest: "GIFT City", time: "08:10", icon: Sparkles },
  { label: "Mahatma Mandir -> GIFT City", origin: "Mahatma Mandir", dest: "GIFT City", time: "09:00", icon: Building2 },
  { label: "Sabarmati -> BRTS Hub", origin: "Sabarmati", dest: "BRTS Zonal Hub", time: "10:00", icon: Navigation },
  { label: "Paldi -> AMTS", origin: "Paldi", dest: "AMTS Central Terminal", time: "12:00", icon: MapPin },
  { label: "GIFT Office -> Old High Court", origin: "GIFT City Office Hub", dest: "Old High Court", time: "17:00", icon: Sparkles }
];

export default function Planner({ onRouteFound, initialOrigin = "", initialDestination = "" }) {
  const [origin, setOrigin] = useState(initialOrigin || "APMC");
  const [destination, setDestination] = useState(initialDestination || "GIFT City");
  const [time, setTime] = useState("08:00");
  const [isLeaveBy, setIsLeaveBy] = useState(false);
  const [accessibleOnly, setAccessibleOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [stationsList, setStationsList] = useState([]);

  // Fetch stations for autocomplete
  useEffect(() => {
    fetch("http://localhost:8000/api/network")
      .then(res => res.json())
      .then(data => {
        if (data.stations) {
          setStationsList(data.stations.map(s => s.name_en));
        }
      })
      .catch(console.error);
  }, []);

  const handleSwap = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  const handleQuickChip = (chip) => {
    setOrigin(chip.origin);
    setDestination(chip.dest);
    setTime(chip.time);
  };

  const handleVoice = async () => {
    setIsRecording(true);
    try {
      const res = await fetch("http://localhost:8000/api/voice", { method: "POST" });
      const data = await res.json();
      if (data.origin) setOrigin("APMC");
      if (data.destination) setDestination("GIFT City");
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsRecording(false), 800);
    }
  };

  const handlePlan = async () => {
    if (!origin || !destination) return;
    setLoading(true);

    try {
      const originId = origin.trim().toLowerCase().replace(/\s+/g, "_");
      const destId = destination.trim().toLowerCase().replace(/\s+/g, "_");

      const res = await fetch("http://localhost:8000/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin_id: originId,
          destination_id: destId,
          time: time.length === 5 ? `${time}:00` : time,
          accessibility: accessibleOnly
        })
      });

      if (!res.ok) {
        throw new Error("Route not found");
      }

      const data = await res.json();
      onRouteFound(data);
    } catch (err) {
      console.error(err);
      alert("No route found between selected points. Try typing station names like 'APMC', 'Old High Court', 'GNLU', or 'GIFT City'.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3.5">
      <datalist id="station-list">
        {stationsList.map((s, idx) => (
          <option key={idx} value={s} />
        ))}
        {/* Popular Locations / POIs */}
        <option value="Ahmedabad Airport" />
        <option value="Akshardham Temple" />
        <option value="Alpha One Mall" />
        <option value="Civil Hospital" />
        <option value="Gujarat University" />
        <option value="IIM Ahmedabad" />
        <option value="Iskcon Temple" />
        <option value="Kankaria Lake" />
        <option value="Law Garden" />
        <option value="Palladium Mall" />
        <option value="Prahlad Nagar Garden" />
        <option value="Sabarmati Riverfront" />
        <option value="Science City" />
        <option value="SG Highway" />
        <option value="Sidi Saiyyed Mosque" />
        <option value="Vastrapur Lake" />
        <option value="GIFT City Office Hub" />
        <option value="Ahmedabad Railway Station" />
      </datalist>

      {/* Origin & Destination Card */}
      <div className="relative bg-surface border border-border rounded-2xl p-3 shadow-xs">
        {/* Origin Field */}
        <div className="relative mb-2.5">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-emerald-500">
            <Navigation size={18} />
          </div>
          <input
            type="text"
            list="station-list"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            placeholder="Origin station (e.g. APMC, Thaltej)"
            className="w-full bg-surface-hover/60 border border-border rounded-xl py-3 pl-10 pr-10 text-foreground placeholder-foreground-muted text-[15px] focus:outline-none focus:ring-2 focus:ring-primary/25 focus:border-primary transition-all font-medium"
          />
        </div>

        {/* Swap Button */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10">
          <button
            type="button"
            onClick={handleSwap}
            className="w-8 h-8 rounded-full bg-surface border border-border shadow-md flex items-center justify-center text-foreground-muted hover:text-primary hover:border-primary transition-all active:scale-95 cursor-pointer"
            aria-label="Swap origin and destination"
          >
            <ArrowUpDown size={15} />
          </button>
        </div>

        {/* Destination Field */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-rose-500">
            <MapPin size={18} />
          </div>
          <input
            type="text"
            list="station-list"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="Destination (e.g. GIFT City, Vastral)"
            className="w-full bg-surface-hover/60 border border-border rounded-xl py-3 pl-10 pr-10 text-foreground placeholder-foreground-muted text-[15px] focus:outline-none focus:ring-2 focus:ring-primary/25 focus:border-primary transition-all font-medium"
          />
        </div>
      </div>

      {/* Quick Shortcut Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar text-xs">
        {QUICK_CHIPS.map((chip) => {
          const Icon = chip.icon;
          return (
            <button
              key={chip.label}
              onClick={() => handleQuickChip(chip)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-surface border border-border hover:border-primary/40 text-foreground-muted hover:text-foreground text-xs font-semibold whitespace-nowrap transition-all shadow-2xs active:scale-95 cursor-pointer"
            >
              <Icon size={12} className="text-primary" />
              <span>{chip.label}</span>
            </button>
          );
        })}
      </div>

      {/* Time & Leave-by Controls */}
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-foreground-muted">
            <Clock size={16} />
          </div>
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            className="w-full bg-surface border border-border rounded-xl py-2.5 pl-9 pr-3 text-foreground font-semibold text-sm focus:outline-none focus:ring-2 focus:ring-primary/25 focus:border-primary"
          />
        </div>

        {/* Voice Input Button */}
        <button
          onClick={handleVoice}
          disabled={typeof navigator !== 'undefined' && !navigator.onLine}
          className={`px-3 py-2.5 rounded-xl border flex items-center gap-1.5 text-xs font-bold transition-all ${
            (typeof navigator !== 'undefined' && !navigator.onLine)
              ? "bg-surface border-border text-foreground-muted cursor-not-allowed opacity-50"
              : isRecording
              ? "bg-rose-500 text-white border-rose-600 animate-pulse cursor-pointer"
              : "bg-surface border-border text-foreground hover:bg-surface-hover cursor-pointer"
          }`}
          title={(typeof navigator !== 'undefined' && !navigator.onLine) ? "Voice needs internet; type instead" : "Voice input"}
          aria-label="Voice input"
        >
          {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
          <span className="hidden sm:inline">Voice</span>
        </button>

        {/* Accessibility Toggle */}
        <button
          onClick={() => setAccessibleOnly(!accessibleOnly)}
          className={`p-2.5 rounded-xl border flex items-center justify-center transition-all cursor-pointer ${
            accessibleOnly
              ? "bg-primary text-white border-primary"
              : "bg-surface border-border text-foreground-muted hover:text-foreground"
          }`}
          title="Step-free accessibility only"
          aria-label="Toggle accessible step-free routes"
        >
          <Accessibility size={18} />
        </button>
      </div>

      {/* Action Button */}
      <button
        onClick={handlePlan}
        disabled={loading}
        className="w-full py-3.5 px-4 rounded-xl bg-primary hover:bg-primary/95 text-white font-extrabold text-sm md:text-base shadow-md shadow-primary/25 hover:shadow-lg transition-all active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer"
      >
        {loading ? (
          <span className="animate-pulse">Finding Best Journey...</span>
        ) : (
          <>
            <Search size={18} />
            <span>Find Routes</span>
          </>
        )}
      </button>
    </div>
  );
}
