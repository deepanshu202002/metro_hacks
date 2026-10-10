"use client";

import { useState, useEffect } from "react";
import { Clock, Train, Bus, AlertCircle, RefreshCw, Search, ChevronRight } from "lucide-react";

export default function TimingsBoard() {
  const [stations, setStations] = useState<any[]>([]);
  const [selectedStationId, setSelectedStationId] = useState("old_high_court");
  const [boardData, setBoardData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/network")
      .then((res) => res.json())
      .then((data) => {
        setStations(data.stations || []);
      })
      .catch(console.error);
  }, []);

  const loadDepartures = async (sId) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/departures?station_id=${sId}`);
      const data = await res.json();
      setBoardData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedStationId) {
      loadDepartures(selectedStationId);
    }
  }, [selectedStationId]);

  const filteredStations = stations.filter(
    (s) =>
      s.name_en.toLowerCase().includes(searchFilter.toLowerCase()) ||
      (s.name_gu && s.name_gu.includes(searchFilter)) ||
      (s.name_hi && s.name_hi.includes(searchFilter))
  );

  return (
    <div className="h-full flex flex-col p-4 md:p-6 space-y-4 overflow-y-auto">
      {/* Top Title & Refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl md:text-2xl font-black text-foreground tracking-tight">
            Live Station Departures
          </h2>
          <p className="text-xs text-foreground-muted mt-0.5">
            Real-time countdowns & next train boards for all 54 stations
          </p>
        </div>
        <button
          onClick={() => loadDepartures(selectedStationId)}
          className="p-2 rounded-xl bg-surface border border-border text-foreground hover:bg-surface-hover transition-all cursor-pointer shadow-2xs"
          aria-label="Refresh departures"
        >
          <RefreshCw size={16} className={loading ? "animate-spin text-primary" : ""} />
        </button>
      </div>

      {/* Station Selector / Autocomplete */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-foreground-muted">
          <Search size={16} />
        </div>
        <input
          type="text"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          placeholder="Search station (e.g. Old High Court, Motera, GIFT City)..."
          className="w-full bg-surface border border-border rounded-xl py-2.5 pl-9 pr-4 text-xs md:text-sm text-foreground placeholder-foreground-muted focus:outline-none focus:ring-2 focus:ring-primary/25"
        />
        {searchFilter && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-surface border border-border rounded-xl shadow-xl z-30 max-h-48 overflow-y-auto">
            {filteredStations.map((st) => (
              <button
                key={st.id}
                onClick={() => {
                  setSelectedStationId(st.id);
                  setSearchFilter("");
                }}
                className="w-full text-left px-3.5 py-2 hover:bg-surface-hover text-xs font-semibold flex items-center justify-between cursor-pointer border-b border-border/40"
              >
                <span>{st.name_en}</span>
                <span className="text-[10px] text-foreground-muted">{st.lines?.join(" • ")}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Current Station Header Banner */}
      {boardData?.station && (
        <div className="bg-surface border border-border rounded-2xl p-4 shadow-xs">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-foreground">
                  {boardData.station.name_en}
                </h3>
                {boardData.station.interchange && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-primary/10 text-primary uppercase">
                    Interchange Hub
                  </span>
                )}
              </div>
              <p className="text-xs text-foreground-muted mt-0.5">
                {boardData.station.name_gu} • {boardData.station.name_hi}
              </p>
            </div>
            <div className="flex gap-1">
              {boardData.station.lines?.map((line) => (
                <span
                  key={line}
                  className="px-2 py-0.5 rounded text-[10px] font-bold text-white shadow-2xs"
                  style={{
                    backgroundColor:
                      line === "Blue"
                        ? "#1D6FD8"
                        : line === "Red"
                        ? "#D7263D"
                        : line === "Yellow"
                        ? "#F2B705"
                        : "#7C3AED"
                  }}
                >
                  {line} Line
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* GNLU Advisory Banner */}
      {boardData?.station?.id === "gnlu" && (
        <div className="bg-primary/10 border border-primary/20 rounded-xl p-4 mt-1 text-primary">
          <div className="flex items-start gap-2">
            <AlertCircle size={18} className="shrink-0 mt-0.5" />
            <div className="text-xs space-y-1">
              <p className="font-bold">GNLU ↔ GIFT City Connection Info</p>
              <ul className="list-disc pl-4 space-y-0.5">
                <li><span className="font-semibold">Feeder Bus:</span> Free connector bus operates every 30 minutes.</li>
                <li><span className="font-semibold">Metro Service:</span> Trains operate every 1 hour during peak periods (07:00–10:00 and 16:00–19:00).</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Departure Board Rows */}
      <div className="space-y-2.5">
        {boardData?.departures?.length > 0 ? (
          boardData.departures.map((dep, idx) => (
            <div
              key={idx}
              className="bg-surface border border-border rounded-xl p-3.5 flex items-center justify-between hover:bg-surface-hover/70 transition-all shadow-2xs"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-surface-hover flex items-center justify-center font-bold text-foreground">
                  <Train size={16} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-foreground">
                      Towards {dep.destination}
                    </span>
                    {dep.is_last_service && (
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-extrabold bg-rose-500/10 text-rose-600 border border-rose-500/20">
                        LAST SERVICE
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-foreground-muted flex items-center gap-2 mt-0.5">
                    <span>{dep.line}</span>
                    <span>•</span>
                    <span>{dep.service}</span>
                    <span>•</span>
                    <span className="tabular-nums font-semibold">{dep.departure_time}</span>
                  </div>
                </div>
              </div>

              {/* Countdown Pill */}
              <div className="text-right">
                <div className="text-base font-black text-primary tabular-nums">
                  {dep.wait_minutes === 0 ? "Now" : `${dep.wait_minutes} min`}
                </div>
                <div className="text-[10px] text-foreground-muted font-medium">
                  {dep.wait_minutes === 0 ? "At Platform" : "Scheduled"}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-8 text-center bg-surface border border-border rounded-2xl text-foreground-muted text-xs">
            {loading ? "Loading live schedule..." : "No upcoming departures scheduled for this station right now."}
          </div>
        )}
      </div>
    </div>
  );
}
