"use client";

import { useEffect, useState, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import SchematicMap from "./SchematicMap";

// Fix Leaflet default marker icons in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const ahmedabadCenter: [number, number] = [23.0800, 72.6000];

const LINE_COLORS: Record<string, string> = {
  Blue: "#1D6FD8",
  Red: "#D7263D",
  Yellow: "#F2B705",
  Violet: "#7C3AED",
  BRTS: "#0EA5E9",
  Direct: "#7C3AED",
  walk: "#64748B",
  cab: "#F97316",
  shuttle: "#10B981"
};

export default function MapComponent({
  routeData,
  selectedOption = "metro_only",
  theme = "light",
  onSelectStation = null,
  congestionData = null
}) {
  const [network, setNetwork] = useState<any>(null);
  const [mapMode, setMapMode] = useState("street"); // "street" | "schematic"
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    // Check initial online status
    if (typeof window !== "undefined") {
      setIsOffline(!navigator.onLine);
      if (!navigator.onLine) setMapMode("schematic");
      
      const handleOnline = () => setIsOffline(false);
      const handleOffline = () => { setIsOffline(true); setMapMode("schematic"); };
      
      window.addEventListener("online", handleOnline);
      window.addEventListener("offline", handleOffline);
      return () => {
        window.removeEventListener("online", handleOnline);
        window.removeEventListener("offline", handleOffline);
      };
    }
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/api/network")
      .then((res) => res.json())
      .then((data) => setNetwork(data))
      .catch((err) => console.error("Error loading network:", err));
  }, []);

  const activeLegs = useMemo(() => {
    if (!routeData) return [];
    if (routeData[selectedOption]?.legs) return routeData[selectedOption].legs;
    if (routeData.legs) return routeData.legs;
    return [];
  }, [routeData, selectedOption]);

  const tileUrl = theme === "dark"
    ? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

  if (mapMode === "schematic") {
    return (
      <div className="h-full w-full bg-background relative z-0">
        <SchematicMap network={network} activeLegs={activeLegs} />
        {/* Toggle Mode Button */}
        <div className="absolute bottom-4 left-4 z-[500]">
          <button
            onClick={() => setMapMode("street")}
            disabled={isOffline}
            className={`px-4 py-2 rounded-xl text-xs font-bold shadow-md transition-all ${
              isOffline ? "bg-surface-hover text-foreground-muted cursor-not-allowed" : "bg-primary text-white hover:bg-primary/90"
            }`}
          >
            Switch to Street Map {isOffline && "(Offline)"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-background relative z-0">
      <MapContainer
        center={ahmedabadCenter}
        zoom={12}
        style={{ height: "100%", width: "100%", zIndex: 0 }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> & OpenStreetMap'
          url={tileUrl}
        />

        {/* Base Network Polylines */}
        {network && network.lines && (
          <>
            {/* Red Line */}
            {network.lines.Red?.map((segment, i) => (
              <Polyline
                key={`red-${i}`}
                positions={segment}
                pathOptions={{
                  color: LINE_COLORS.Red,
                  weight: activeLegs.length > 0 ? 3 : 5,
                  opacity: activeLegs.length > 0 ? 0.35 : 0.85,
                  lineCap: "round"
                }}
              />
            ))}

            {/* Blue Line */}
            {network.lines.Blue?.map((segment, i) => (
              <Polyline
                key={`blue-${i}`}
                positions={segment}
                pathOptions={{
                  color: LINE_COLORS.Blue,
                  weight: activeLegs.length > 0 ? 3 : 5,
                  opacity: activeLegs.length > 0 ? 0.35 : 0.85,
                  lineCap: "round"
                }}
              />
            ))}

            {/* Yellow Line (Gandhinagar Phase 2) */}
            {network.lines.Yellow?.map((segment, i) => (
              <Polyline
                key={`yellow-${i}`}
                positions={segment}
                pathOptions={{
                  color: LINE_COLORS.Yellow,
                  weight: activeLegs.length > 0 ? 3 : 5,
                  opacity: activeLegs.length > 0 ? 0.35 : 0.85,
                  lineCap: "round"
                }}
              />
            ))}

            {/* Violet Line (GIFT City Branch) */}
            {network.lines.Violet?.map((segment, i) => (
              <Polyline
                key={`violet-${i}`}
                positions={segment}
                pathOptions={{
                  color: LINE_COLORS.Violet,
                  weight: activeLegs.length > 0 ? 3.5 : 5,
                  opacity: activeLegs.length > 0 ? 0.4 : 0.9,
                  lineCap: "round"
                }}
              />
            ))}

            {/* BRTS Feeder Corridor */}
            {network.lines.BRTS?.map((segment, i) => (
              <Polyline
                key={`brts-${i}`}
                positions={segment}
                pathOptions={{
                  color: LINE_COLORS.BRTS,
                  weight: 2.5,
                  dashArray: "6, 8",
                  opacity: 0.4
                }}
              />
            ))}
          </>
        )}

        {/* Base Stations Markers */}
        {network && network.stations?.map((st) => {
          const isInterchange = st.interchange;
          const primaryLine = st.lines?.[0] || "Red";
          const lineColor = LINE_COLORS[primaryLine] || "#3B4BDC";

          return (
            <CircleMarker
              key={st.id}
              center={[st.lat, st.lng]}
              radius={isInterchange ? 6.5 : 4}
              pathOptions={{
                color: isInterchange ? "#0F172A" : lineColor,
                fillColor: "#FFFFFF",
                fillOpacity: 1,
                weight: isInterchange ? 2.5 : 1.8
              }}
              eventHandlers={{
                click: () => { if (typeof onSelectStation === 'function') onSelectStation(st); }
              }}
            >
              <Popup className="custom-popup">
                <div className="p-1 min-w-[160px]">
                  <div className="font-bold text-sm text-foreground flex items-center gap-1.5">
                    <span>{st.name_en}</span>
                    {isInterchange && (
                      <span className="text-[10px] bg-primary/10 text-primary font-bold px-1.5 py-0.2 rounded">
                        Interchange
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-foreground-muted mt-0.5">
                    {st.name_gu} • {st.name_hi}
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {st.lines?.map((l) => (
                      <span
                        key={l}
                        className="text-[10px] font-bold px-1.5 py-0.5 rounded text-white"
                        style={{ backgroundColor: LINE_COLORS[l] || "#64748B" }}
                      >
                        {l} Line
                      </span>
                    ))}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* Active Route Legs (Glowing and Highlighted) */}
        {activeLegs.map((leg, idx) => {
          if (!leg.path_coords || leg.path_coords.length < 2) return null;
          const legColor = leg.mode === "walk"
            ? LINE_COLORS.walk
            : leg.mode === "cab"
            ? LINE_COLORS.cab
            : leg.mode === "shuttle"
            ? LINE_COLORS.shuttle
            : LINE_COLORS[leg.line] || LINE_COLORS.Blue;

          const isWalk = leg.mode === "walk";

          return (
            <span key={`active-leg-${idx}`}>
              {/* Glow Polyline */}
              {!isWalk && (
                <Polyline
                  positions={leg.path_coords}
                  pathOptions={{
                    color: legColor,
                    weight: 10,
                    opacity: 0.35,
                    lineCap: "round"
                  }}
                />
              )}
              {/* Core Active Polyline */}
              <Polyline
                positions={leg.path_coords}
                pathOptions={{
                  color: legColor,
                  weight: isWalk ? 4 : 6,
                  dashArray: isWalk ? "7, 9" : undefined,
                  opacity: 1,
                  lineCap: "round"
                }}
              />
            </span>
          );
        })}
      </MapContainer>

      {/* Floating Transit Legend & Toggle */}
      <div className="absolute top-4 right-4 z-[500] bg-surface/90 backdrop-blur-md border border-border p-3 rounded-2xl shadow-lg flex flex-col gap-2 pointer-events-auto">
        <div className="text-[11px] font-bold text-foreground mb-0.5 uppercase tracking-wider flex justify-between items-center">
          <span>Metro Network</span>
          <button onClick={() => setMapMode("schematic")} className="text-primary hover:underline ml-2">Schematic</button>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground-muted">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: LINE_COLORS.Blue }} /> Blue: Thaltej-Vastral
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground-muted">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: LINE_COLORS.Red }} /> Red: APMC-Motera
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground-muted">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: LINE_COLORS.Yellow }} /> Yellow: Gandhinagar
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground-muted">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: LINE_COLORS.Violet }} /> Violet: GIFT City
        </div>
      </div>
    </div>
  );
}
