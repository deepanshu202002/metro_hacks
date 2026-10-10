"use client";

import React, { useMemo } from 'react';

const LINE_COLORS: Record<string, string> = {
  Blue: "#1D6FD8",
  Red: "#D7263D",
  Yellow: "#F2B705",
  Violet: "#7C3AED",
  BRTS: "#0EA5E9"
};

export default function SchematicMap({ network, activeLegs }: any) {
  // A simple auto-scaling SVG diagram based on lat/lng coordinates
  const { minLat, maxLat, minLng, maxLng } = useMemo(() => {
    let minLat = 90, maxLat = -90, minLng = 180, maxLng = -180;
    if (network?.stations) {
      network.stations.forEach((s: any) => {
        if (s.lat < minLat) minLat = s.lat;
        if (s.lat > maxLat) maxLat = s.lat;
        if (s.lng < minLng) minLng = s.lng;
        if (s.lng > maxLng) maxLng = s.lng;
      });
    }
    return { minLat, maxLat, minLng, maxLng };
  }, [network]);

  const mapLat = (lat: number) => 100 - ((lat - minLat) / (maxLat - minLat)) * 100;
  const mapLng = (lng: number) => ((lng - minLng) / (maxLng - minLng)) * 100;

  if (!network) return <div className="p-4 text-foreground">Loading Schematic...</div>;

  return (
    <div className="w-full h-full bg-background overflow-hidden relative">
      <div className="absolute inset-0 p-4">
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet" className="w-full h-full">
          {/* Edges */}
          {Object.entries(network.lines || {}).map(([line, segments]: [string, any]) => (
            <g key={line}>
              {segments.map((segment: any, i: number) => {
                const [p1, p2] = segment;
                const x1 = mapLng(p1[1]);
                const y1 = mapLat(p1[0]);
                const x2 = mapLng(p2[1]);
                const y2 = mapLat(p2[0]);
                
                // Highlight if active
                const isActive = activeLegs?.some((leg: any) => 
                  leg.line === line && leg.path_coords?.some((c: any) => c[0] === p1[0] && c[1] === p1[1])
                );

                return (
                  <line 
                    key={i} 
                    x1={x1} y1={y1} x2={x2} y2={y2} 
                    stroke={LINE_COLORS[line] || "#ccc"} 
                    strokeWidth={isActive ? "2" : "0.5"}
                    strokeOpacity={isActive ? "1" : "0.4"}
                    strokeDasharray={line === "BRTS" ? "1,1" : ""}
                  />
                );
              })}
            </g>
          ))}
          
          {/* Stations */}
          {network.stations?.map((st: any) => {
            const cx = mapLng(st.lng);
            const cy = mapLat(st.lat);
            const isInterchange = st.interchange;
            
            const isActive = activeLegs?.some((leg: any) => 
              leg.stations?.some((ls: any) => ls.id === st.id)
            );

            return (
              <g key={st.id}>
                <circle 
                  cx={cx} 
                  cy={cy} 
                  r={isInterchange ? 1.5 : 0.8}
                  fill={isActive ? "#14B8A6" : "#fff"}
                  stroke={LINE_COLORS[st.lines?.[0] || "Red"]}
                  strokeWidth="0.4"
                />
                {isActive && (
                  <text x={cx + 2} y={cy + 1} fontSize="2.5" fill="#14B8A6" fontWeight="bold">
                    {st.name_en}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
