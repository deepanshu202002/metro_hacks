"use client";

import { useEffect, useState } from "react";
import { X, Database, CheckCircle2, AlertTriangle, ExternalLink } from "lucide-react";

export default function DataSourcesModal({ isOpen, onClose }) {
  const [sources, setSources] = useState<any[]>([]);

  useEffect(() => {
    if (isOpen) {
      fetch("http://localhost:8000/api/data-sources")
        .then((res) => res.json())
        .then((data) => setSources(data.datasets || []))
        .catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-surface border border-border w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-4 md:p-5 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
              <Database size={18} />
            </div>
            <div>
              <h2 className="text-base md:text-lg font-black text-foreground">
                Data Sources & Verification Audit
              </h2>
              <p className="text-xs text-foreground-muted">
                Transparent inventory of real vs. calibrated datasets
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-foreground-muted hover:text-foreground hover:bg-surface-hover cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Sources List */}
        <div className="p-4 md:p-5 overflow-y-auto space-y-3">
          {sources.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-xl border border-border bg-surface-hover/50 space-y-1.5 text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-extrabold text-foreground text-sm">
                  {item.name}
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase shrink-0 ${
                    item.verified
                      ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-600 border border-amber-500/20"
                  }`}
                >
                  {item.type}
                </span>
              </div>
              <div className="text-foreground-muted">
                <strong>Source:</strong> {item.source}
              </div>
              <div className="flex items-center justify-between text-[11px] text-foreground-muted pt-1">
                <span>Date: {item.source_date}</span>
                <span className="flex items-center gap-1 font-semibold">
                  {item.verified ? (
                    <>
                      <CheckCircle2 size={12} className="text-emerald-500" />
                      <span className="text-emerald-600">Verified official</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle size={12} className="text-amber-500" />
                      <span className="text-amber-600">Synthetic / Calibration</span>
                    </>
                  )}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-3.5 border-t border-border bg-surface flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-primary text-white font-bold text-xs hover:bg-primary/90 transition-all cursor-pointer"
          >
            Close Audit
          </button>
        </div>
      </div>
    </div>
  );
}
