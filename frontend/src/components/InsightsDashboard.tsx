"use client";

import { useState, useEffect } from "react";
import {
  Users,
  Activity,
  AlertTriangle,
  TrendingUp,
  Clock,
  Sparkles,
  Download,
  Building,
  ShieldAlert,
  ArrowRight,
  Sliders,
  Calendar,
  Layers
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceArea
} from "recharts";

export default function InsightsDashboard({ lang = "en", role = "user" }) {
  const [dayType, setDayType] = useState("weekday");
  const [hour, setHour] = useState(9);
  const [overview, setOverview] = useState<any>(null);
  const [topCongested, setTopCongested] = useState<any[]>([]);
  const [peakHoursData, setPeakHoursData] = useState<any[]>([]);
  const [odFlows, setOdFlows] = useState<any[]>([]);
  const [forecast, setForecast] = useState<any>(null);
  const [interchanges, setInterchanges] = useState<any>(null);
  const [delays, setDelays] = useState<any>(null);
  const [clusters, setClusters] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [narratedInsights, setNarratedInsights] = useState<any>(null);

  // Simulator state
  const [simAttendance, setSimAttendance] = useState(85000);
  const [simExtraTrains, setSimExtraTrains] = useState(4);
  const [simResult, setSimResult] = useState<any>(null);

  // Load Overview & Top Congested on hour/dayType change
  useEffect(() => {
    fetch(`http://localhost:8000/api/analytics/overview?day_type=${dayType}&hour=${hour}`)
      .then((r) => r.json())
      .then((data) => setOverview(data))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/top-congested?day_type=${dayType}&hour=${hour}&limit=10`)
      .then((r) => r.json())
      .then((data) => setTopCongested(data.ranking || []))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/forecast?station_id=old_high_court&current_hour=${hour}&day_type=${dayType}`)
      .then((r) => r.json())
      .then((data) => setForecast(data))
      .catch(console.error);
  }, [dayType, hour]);

  // Load General Charts & Tables once
  useEffect(() => {
    fetch(`http://localhost:8000/api/analytics/peak-hours?day_type=${dayType}`)
      .then((r) => r.json())
      .then((data) => setPeakHoursData(data.chart || []))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/od-flows`)
      .then((r) => r.json())
      .then((data) => setOdFlows(data.flows || []))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/interchanges`)
      .then((r) => r.json())
      .then((data) => setInterchanges(data))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/delays`)
      .then((r) => r.json())
      .then((data) => setDelays(data))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/clusters`)
      .then((r) => r.json())
      .then((data) => setClusters(data))
      .catch(console.error);

    fetch(`http://localhost:8000/api/analytics/anomalies`)
      .then((r) => r.json())
      .then((data) => setAnomalies(data.anomalies || []))
      .catch(console.error);
  }, [dayType]);

  // Load Narrated Insights
  useEffect(() => {
    fetch(`http://localhost:8000/api/analytics/insights?lang=${lang}`)
      .then((r) => r.json())
      .then((data) => setNarratedInsights(data))
      .catch(console.error);
  }, [lang]);

  // Run Simulator
  const runSimulation = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/analytics/event-simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          attendance: simAttendance,
          extra_trains: simExtraTrains,
          headway_minutes: 5
        })
      });
      const data = await res.json();
      setSimResult(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [simAttendance, simExtraTrains]);

  // CSV Export
  const exportCsv = () => {
    if (!topCongested.length) return;
    const headers = "Rank,Station,Boardings,CrowdLevel,Reason\n";
    const rows = topCongested
      .map((r) => `${r.rank},"${r.name_en}",${r.boardings},${r.crowd_level},"${r.reason_tag}"`)
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ahmedabad_metro_analytics_${dayType}_${hour}h.csv`;
    a.click();
  };

  return (
    <div className="h-full flex flex-col p-4 md:p-6 space-y-6 overflow-y-auto pb-20">
      {/* Permanent Synthetic Calibration Badge */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-amber-500/10 border border-amber-500/25 p-3.5 rounded-2xl">
        <div className="flex items-center gap-2 text-xs font-semibold text-amber-800 dark:text-amber-300">
          <ShieldAlert size={16} className="shrink-0" />
          <span>Synthetic data calibrated to published ridership totals (~1.5–2.0 lakh/day), not official station-level gate data.</span>
        </div>
        <button
          onClick={exportCsv}
          className="px-3 py-1.5 rounded-xl bg-surface border border-border text-foreground hover:bg-surface-hover text-xs font-bold flex items-center gap-1.5 shadow-2xs shrink-0 cursor-pointer"
        >
          <Download size={13} />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Control Bar: Day Type & Time of Day Slider */}
      <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 font-bold text-sm text-foreground">
            <Sliders size={16} className="text-primary" />
            <span>Operational Scenario & Time Window</span>
          </div>
          {/* Day Type Selector */}
          <div className="flex items-center gap-1 bg-surface-hover p-1 rounded-xl border border-border text-xs font-bold">
            {[
              { id: "weekday", label: "Weekday" },
              { id: "weekend", label: "Weekend" },
              { id: "event_day", label: "Event Day (Match)" },
              { id: "rain_day", label: "Rain Day" }
            ].map((dt) => (
              <button
                key={dt.id}
                onClick={() => setDayType(dt.id)}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  dayType === dt.id
                    ? "bg-primary text-white shadow-xs"
                    : "text-foreground-muted hover:text-foreground"
                }`}
              >
                {dt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Hour Slider */}
        <div className="flex items-center gap-4 pt-1">
          <span className="text-xs font-bold text-foreground-muted w-16">
            Time: <span className="text-foreground tabular-nums font-extrabold">{String(hour).padStart(2, '0')}:00</span>
          </span>
          <input
            type="range"
            min="6"
            max="22"
            value={hour}
            onChange={(e) => setHour(parseInt(e.target.value))}
            className="flex-1 accent-primary cursor-pointer"
          />
          <span className="text-[11px] font-semibold text-foreground-muted">
            {hour >= 8 && hour <= 10 ? "AM Peak Window" : hour >= 17 && hour <= 19 ? "PM Peak Window" : "Off-Peak"}
          </span>
        </div>
      </div>

      {/* Panel 1: KPI Cards */}
      {overview && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs">
            <div className="text-xs font-bold text-foreground-muted flex items-center justify-between">
              <span>Daily Ridership</span>
              <Users size={15} className="text-primary" />
            </div>
            <div className="text-2xl font-black text-foreground tabular-nums mt-1">
              {overview.daily_ridership.toLocaleString()}
            </div>
            <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold mt-1">
              Calibrated ~1.78 Lakh Target
            </div>
          </div>

          <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs">
            <div className="text-xs font-bold text-foreground-muted flex items-center justify-between">
              <span>Current Hour Load</span>
              <Activity size={15} className="text-amber-500" />
            </div>
            <div className="text-2xl font-black text-foreground tabular-nums mt-1">
              {overview.peak_hour_load.toLocaleString()}
            </div>
            <div className="text-[10px] text-foreground-muted font-medium mt-1">
              Boardings at {String(hour).padStart(2, '0')}:00
            </div>
          </div>

          <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs">
            <div className="text-xs font-bold text-foreground-muted flex items-center justify-between">
              <span>Busiest Station Now</span>
              <Building size={15} className="text-rose-500" />
            </div>
            <div className="text-lg font-black text-foreground truncate mt-1">
              {overview.busiest_station}
            </div>
            <div className="text-[10px] text-foreground-muted font-semibold mt-1">
              {overview.busiest_station_boardings} pax/hr
            </div>
          </div>

          <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs">
            <div className="text-xs font-bold text-foreground-muted flex items-center justify-between">
              <span>GIFT City Commuters</span>
              <Building size={15} className="text-violet-500" />
            </div>
            <div className="text-2xl font-black text-foreground tabular-nums mt-1">
              {overview.gift_city_commuters.toLocaleString()}
            </div>
            <div className="text-[10px] text-emerald-600 font-bold mt-1">
              Financial SEZ Corridor
            </div>
          </div>
        </div>
      )}

      {/* Panel 12: Insight Narrator (LLM/Grounded Insights) */}
      {role === "operator" && narratedInsights && (
        <div className="bg-surface border border-primary/30 p-4 rounded-2xl shadow-xs space-y-2.5">
          <div className="flex items-center gap-2 text-sm font-extrabold text-primary">
            <Sparkles size={16} />
            <span>Automated Operational Insights (Grounded in Verified Data)</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            {narratedInsights.insights?.map((text, idx) => (
              <div key={idx} className="p-2.5 bg-surface-hover/70 rounded-xl border border-border flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                <span className="font-medium text-foreground">{text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Panel 4: Peak Hours Chart (Recharts) */}
      {role === "operator" && (
      <div className="bg-surface border border-border p-4 md:p-5 rounded-2xl shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
            <TrendingUp size={16} className="text-primary" />
            <span>Hourly Boardings by Line (AM/PM Peaks Highlighted)</span>
          </h3>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={peakHoursData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Area type="monotone" dataKey="Blue" stackId="1" stroke="#1D6FD8" fill="#1D6FD8" fillOpacity={0.6} />
              <Area type="monotone" dataKey="Red" stackId="1" stroke="#D7263D" fill="#D7263D" fillOpacity={0.6} />
              <Area type="monotone" dataKey="Yellow" stackId="1" stroke="#F2B705" fill="#F2B705" fillOpacity={0.6} />
              <Area type="monotone" dataKey="Violet" stackId="1" stroke="#7C3AED" fill="#7C3AED" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      )}


      {/* Panel 3: Top-10 Congested Stations Ranking */}
      <div className="bg-surface border border-border p-4 md:p-5 rounded-2xl shadow-xs space-y-3">
        <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-500" />
          <span>Top-10 Station Congestion Ranking ({String(hour).padStart(2, '0')}:00)</span>
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-border text-foreground-muted font-bold">
                <th className="py-2 px-2">#</th>
                <th className="py-2 px-3">Station</th>
                <th className="py-2 px-3">Boardings/hr</th>
                <th className="py-2 px-3">Crowd Status</th>
                <th className="py-2 px-3">Archetype / Reason</th>
                <th className="py-2 px-3">Peak Hour</th>
              </tr>
            </thead>
            <tbody>
              {topCongested.map((r) => (
                <tr key={r.rank} className="border-b border-border/40 hover:bg-surface-hover/50 transition-colors">
                  <td className="py-2.5 px-2 font-bold tabular-nums">{r.rank}</td>
                  <td className="py-2.5 px-3 font-semibold text-foreground">{r.name_en}</td>
                  <td className="py-2.5 px-3 font-bold tabular-nums">{r.boardings.toLocaleString()}</td>
                  <td className="py-2.5 px-3">
                    <span
                      className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase"
                      style={{ backgroundColor: `${r.crowd_color}20`, color: r.crowd_color }}
                    >
                      {r.crowd_level}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-foreground-muted">{r.reason_tag}</td>
                  <td className="py-2.5 px-3 font-medium tabular-nums">{r.peak_hour}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Panel 7: Event Impact Simulator (Motera Stadium Match Surge) */}
      {role === "operator" && (
      <div className="bg-surface border border-border p-4 md:p-5 rounded-2xl shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
            <Sliders size={16} className="text-primary" />
            <span>Event Simulator: Narendra Modi Stadium (Motera) Surge</span>
          </h3>
          <span className="text-xs bg-primary/10 text-primary font-bold px-2 py-0.5 rounded">
            Capacity Clearance Model
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3 bg-surface-hover/50 p-3.5 rounded-xl border border-border">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Event Attendance:</span>
                <span className="font-bold tabular-nums">{simAttendance.toLocaleString()} spectators</span>
              </div>
              <input
                type="range"
                min="40000"
                max="120000"
                step="5000"
                value={simAttendance}
                onChange={(e) => setSimAttendance(parseInt(e.target.value))}
                className="w-full accent-primary"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span>Extra Special Trains Deployed:</span>
                <span className="font-bold tabular-nums">{simExtraTrains} rakes</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                value={simExtraTrains}
                onChange={(e) => setSimExtraTrains(parseInt(e.target.value))}
                className="w-full accent-primary"
              />
            </div>
          </div>

          {simResult && (
            <div className="flex flex-col justify-between bg-surface-hover/50 p-3.5 rounded-xl border border-border space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-foreground-muted">Platform Load Reduction:</span>
                <span className="text-base font-black text-emerald-600 dark:text-emerald-400 tabular-nums">
                  -{simResult.load_reduction_pct}%
                </span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-foreground-muted">Est. Crowd Clearance Time:</span>
                <span className="text-base font-black text-foreground tabular-nums">
                  {simResult.expected_clearance_time_min} min
                </span>
              </div>
              <div className="text-[11px] text-foreground-muted pt-1 border-t border-border/60">
                Recommended deployment: deploy at least <strong className="text-primary">{simResult.recommended_extra_trips} extra trips</strong> at 5-minute headways post-match.
              </div>
            </div>
          )}
        </div>
      </div>
      )}

      {/* Panel 5: Top Corridor Flows & Panel 8: Interchange Analytics */}
      {role === "operator" && (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Corridor Flows */}
        <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs space-y-3">
          <h3 className="text-sm font-bold text-foreground">Top Origin-Destination Corridor Flows</h3>
          <div className="space-y-2 text-xs">
            {odFlows.map((flow, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-surface-hover/60 border border-border/40">
                <div className="font-semibold text-foreground">
                  {flow.origin.replace("_", " ")} → {flow.destination.replace("_", " ")}
                </div>
                <div className="text-right">
                  <div className="font-bold tabular-nums">{flow.daily_pax.toLocaleString()} pax/day</div>
                  <div className="text-[10px] text-foreground-muted">{flow.corridor}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interchange Analytics */}
        {interchanges && (
          <div className="bg-surface border border-border p-4 rounded-2xl shadow-xs space-y-3">
            <h3 className="text-sm font-bold text-foreground">Interchange & Feeder Performance</h3>
            <div className="space-y-2.5 text-xs">
              {interchanges.interchanges?.map((hub) => (
                <div key={hub.id} className="p-2.5 rounded-lg bg-surface-hover/60 border border-border/40 flex justify-between items-center">
                  <div>
                    <div className="font-bold text-foreground">{hub.name}</div>
                    <div className="text-[10px] text-foreground-muted">Avg Transfer Wait: {hub.avg_transfer_wait_min} min</div>
                  </div>
                  <div className="text-right font-bold text-emerald-600">
                    {hub.transfer_volume_daily.toLocaleString()} daily pax
                  </div>
                </div>
              ))}
              <div className="p-2.5 rounded-lg bg-primary/5 border border-primary/20 flex justify-between items-center text-xs">
                <div>
                  <div className="font-bold text-primary">GIFT City Shuttle Connection Success</div>
                  <div className="text-[10px] text-foreground-muted">Departs 25m prior to scheduled metro</div>
                </div>
                <div className="font-black text-primary text-sm">
                  {interchanges.gift_city_shuttle?.success_rate_pct}%
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  );
}
