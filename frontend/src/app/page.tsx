"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Train, Clock, BarChart3, Bookmark, AlertCircle, Sparkles } from "lucide-react";

import Header from "@/components/Header";
import Planner from "@/components/Planner";
import CompareOptions from "@/components/CompareOptions";
import TimingsBoard from "@/components/TimingsBoard";
import InsightsDashboard from "@/components/InsightsDashboard";
import SavedPanel from "@/components/SavedPanel";
import DataSourcesModal from "@/components/DataSourcesModal";
import TicketModal from "@/components/TicketModal";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const DEMO_MODE = false;

export default function Home() {
  const [activeTab, setActiveTab] = useState("plan");
  const [lang, setLang] = useState("en");
  const [theme, setTheme] = useState("light");
  const [routeData, setRouteData] = useState<any>(null);
  const [selectedOption, setSelectedOption] = useState<string>("metro_only");
  const [isDataSourcesOpen, setIsDataSourcesOpen] = useState<boolean>(false);
  const [ticketModalData, setTicketModalData] = useState<any>(null);
  const [activeEventAdvisory, setActiveEventAdvisory] = useState<any>(null);

  // Check active events on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/events/active")
      .then((r) => r.json())
      .then((data) => {
        if (data.events && data.events.length > 0) {
          setActiveEventAdvisory(data.events[0]);
        }
      })
      .catch(console.error);
  }, []);

  const handleThemeToggle = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark");
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.setAttribute("data-theme", "light");
    }
  };

  const handleQuickSelectRoute = (destName) => {
    setActiveTab("plan");
  };

  return (
    <div className={`relative h-[100dvh] w-full bg-background text-foreground font-sans flex flex-col overflow-hidden ${theme}`}>
      {/* Top Application Header */}
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        lang={lang}
        onLangChange={setLang}
        theme={theme}
        onThemeToggle={handleThemeToggle}
        onOpenDataSources={() => setIsDataSourcesOpen(true)}
        onOpenDisruptions={() => alert("All 4 Metro Lines (Red, Blue, Yellow, Violet) and GIFT City Shuttles operating with normal headways.")}
      />

      {/* Main Container */}
      <div className="relative flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Left Interactive / Content Sidebar */}
        <div className="w-full md:w-[420px] lg:w-[460px] bg-surface border-r border-border flex flex-col shadow-xl z-20 overflow-hidden shrink-0">
          {/* Active Event Banner (Motera Stadium Match Day) */}
          {activeEventAdvisory && activeTab === "plan" && (
            <div className="px-4 py-2.5 bg-rose-500/10 border-b border-rose-500/20 text-rose-700 dark:text-rose-400 text-xs font-semibold flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                <span>{activeEventAdvisory.title} • Special Trains active</span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-rose-500/20 px-1.5 py-0.5 rounded">
                Advisory
              </span>
            </div>
          )}

          {/* Tab Views */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === "plan" && (
              <div className="p-4 md:p-5 space-y-4">
                <Planner
                  onRouteFound={(data) => {
                    setRouteData(data);
                    if (data?.options?.metro_only) setSelectedOption("metro_only");
                    else if (data?.options?.shuttle) setSelectedOption("shuttle");
                    else if (data?.options?.feeder_bus) setSelectedOption("feeder_bus");
                    else if (data?.options?.cab) setSelectedOption("cab");
                  }}
                />

                {routeData && (
                  <div className="pt-2">
                    <CompareOptions
                      data={routeData}
                      selectedOption={selectedOption}
                      onSelect={setSelectedOption}
                      onOpenTicketModal={(c) => setTicketModalData(c)}
                    />
                  </div>
                )}
              </div>
            )}

            {!DEMO_MODE && activeTab === "timings" && <TimingsBoard />}
            {!DEMO_MODE && activeTab === "insights" && <InsightsDashboard lang={lang} />}
            {!DEMO_MODE && activeTab === "saved" && (
              <SavedPanel onQuickSelectRoute={handleQuickSelectRoute} />
            )}
          </div>

          {/* Mobile Bottom Navigation Bar (Hidden on Desktop) */}
          <div className="md:hidden flex items-center justify-around border-t border-border bg-surface/95 backdrop-blur-md py-2.5 px-2 shrink-0 z-30">
            {[
              { id: "plan", label: "Plan", icon: Train },
              ...(!DEMO_MODE ? [
                { id: "timings", label: "Timings", icon: Clock },
                { id: "insights", label: "Insights", icon: BarChart3 },
                { id: "saved", label: "Saved", icon: Bookmark }
              ] : [])
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition-all cursor-pointer ${
                    isActive ? "text-primary font-bold" : "text-foreground-muted font-medium hover:text-foreground"
                  }`}
                >
                  <Icon size={18} />
                  <span className="text-[10px]">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Main Panel: Full Map */}
        <div className="hidden md:block flex-1 h-full relative z-10">
          <Map
            routeData={routeData?.options}
            selectedOption={selectedOption}
            theme={theme}
          />
        </div>
      </div>

      {/* Modals */}
      <DataSourcesModal
        isOpen={isDataSourcesOpen}
        onClose={() => setIsDataSourcesOpen(false)}
      />

      <TicketModal
        isOpen={!!ticketModalData}
        onClose={() => setTicketModalData(null)}
        ticketData={ticketModalData}
      />
    </div>
  );
}
