"use client";

import { useState, useEffect } from "react";
import { Train, Globe, Moon, Sun, ShieldAlert, Sparkles, Navigation } from "lucide-react";

export default function Header({
  activeTab,
  onTabChange,
  lang,
  onLangChange,
  theme,
  onThemeToggle,
  onOpenDataSources,
  onOpenDisruptions
}) {
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsOffline(!navigator.onLine);
      const handleOnline = () => setIsOffline(false);
      const handleOffline = () => setIsOffline(true);
      window.addEventListener("online", handleOnline);
      window.addEventListener("offline", handleOffline);
      return () => {
        window.removeEventListener("online", handleOnline);
        window.removeEventListener("offline", handleOffline);
      };
    }
  }, []);

  const translations = {
    en: {
      title: "One Journey",
      subtitle: "Ahmedabad & Gandhinagar Metro",
      plan: "Plan",
      timings: "Timings",
      insights: "Insights",
      saved: "Saved",
      sources: "Data Sources",
      normalService: "Normal Service",
      matchAdvisory: "IPL Match Day"
    },
    hi: {
      title: "एक यात्रा",
      subtitle: "अहमदाबाद एवं गांधीनगर मेट्रो",
      plan: "योजना",
      timings: "समय सारणी",
      insights: "एनालिटिक्स",
      saved: "सेव किए",
      sources: "डेटा स्रोत",
      normalService: "सामान्य सेवा",
      matchAdvisory: "मैच दिवस"
    },
    gu: {
      title: "એક યાત્રા",
      subtitle: "અમદાવાદ અને ગાંધીનગર મેટ્રો",
      plan: "પ્લાન",
      timings: "સમયપત્રક",
      insights: "ઇનસાઇટ્સ",
      saved: "સેવ્ડ",
      sources: "ડેટા સ્ત્રોત",
      normalService: "સામાન્ય સેવા",
      matchAdvisory: "મેચ દિવસ"
    }
  };

  const t = (translations as any)[lang] || translations.en;

  return (
    <header className="sticky top-0 z-40 w-full bg-surface/95 backdrop-blur-md border-b border-border shadow-xs px-4 md:px-6 py-2.5 flex items-center justify-between gap-4">
      {/* Brand & Live Status */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => onTabChange("plan")}>
          <div className="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center shadow-md shadow-primary/25">
            <Train size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base md:text-lg tracking-tight text-foreground">
                {t.title}
              </span>
              <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">
                68.3 km
              </span>
            </div>
            <p className="text-[10px] text-foreground-muted hidden md:block">
              {t.subtitle}
            </p>
          </div>
        </div>

        {/* Live Service / Offline Pill */}
        <div className="hidden lg:flex">
          {isOffline ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-xs font-semibold cursor-pointer">
              <ShieldAlert size={14} />
              <span>Offline - using bundled timetable v1</span>
            </div>
          ) : (
            <button
              onClick={onOpenDisruptions}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-semibold hover:bg-emerald-500/20 transition-all cursor-pointer"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>{t.normalService}</span>
            </button>
          )}
        </div>
      </div>

      {/* Center Navigation Tabs (Desktop) */}
      <nav className="hidden md:flex items-center gap-1 bg-surface-hover/80 p-1 rounded-xl border border-border">
        {[
          { id: "plan", label: t.plan },
          { id: "timings", label: t.timings },
          { id: "insights", label: t.insights },
          { id: "saved", label: t.saved }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === tab.id
                ? "bg-surface text-primary shadow-xs border border-border"
                : "text-foreground-muted hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Right Actions: Data Sources, Language, Theme */}
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenDataSources}
          className="text-xs font-medium text-foreground-muted hover:text-foreground px-2.5 py-1.5 rounded-lg border border-border hover:bg-surface-hover transition-colors hidden sm:block"
        >
          {t.sources}
        </button>

        {/* Language Switch */}
        <div className="relative flex items-center bg-surface-hover rounded-lg border border-border p-0.5">
          {["en", "gu", "hi"].map((l) => (
            <button
              key={l}
              onClick={() => onLangChange(l)}
              className={`px-2 py-1 text-[11px] font-bold rounded uppercase transition-all ${
                lang === l
                  ? "bg-surface text-foreground shadow-xs"
                  : "text-foreground-muted hover:text-foreground"
              }`}
            >
              {l}
            </button>
          ))}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={onThemeToggle}
          className="p-2 rounded-lg border border-border bg-surface hover:bg-surface-hover text-foreground-muted hover:text-foreground transition-all"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </header>
  );
}
