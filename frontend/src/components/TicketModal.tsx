"use client";

import { useState } from "react";
import { X, QrCode, CheckCircle2, ShieldCheck, CreditCard, Sparkles } from "lucide-react";

export default function TicketModal({ isOpen, onClose, ticketData }) {
  const [smartCardApplied, setSmartCardApplied] = useState(true);

  if (!isOpen || !ticketData) return null;

  const baseFare = ticketData.fare || 20;
  const discountedFare = smartCardApplied ? Math.max(5, baseFare - 2) : baseFare;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-surface border border-border w-full max-w-sm rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <QrCode size={18} className="text-primary" />
            <h2 className="text-sm font-black text-foreground">Digital Metro Token / QR Ticket</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-foreground-muted hover:text-foreground">
            <X size={16} />
          </button>
        </div>

        {/* Ticket Body */}
        <div className="p-5 flex flex-col items-center space-y-4 text-center">
          {/* Simulated QR Code Canvas */}
          <div className="w-44 h-44 bg-white p-3 rounded-2xl border-2 border-primary/30 shadow-md flex flex-col items-center justify-center relative">
            <div className="grid grid-cols-6 gap-1 w-full h-full p-2 bg-slate-900 rounded-lg">
              {Array.from({ length: 36 }).map((_, i) => (
                <div
                  key={i}
                  className={`rounded-xs ${
                    i % 2 === 0 || i % 7 === 0 || i === 0 || i === 5 || i === 30 || i === 35
                      ? "bg-white"
                      : "bg-slate-900"
                  }`}
                />
              ))}
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 rounded-lg bg-primary text-white flex items-center justify-center text-[10px] font-black shadow-lg">
                OJ
              </div>
            </div>
          </div>

          <div>
            <div className="text-base font-extrabold text-foreground">
              {ticketData.title || "Metro Transit"}
            </div>
            <div className="text-xs text-foreground-muted mt-0.5">
              Valid for single journey across GMRC network
            </div>
          </div>

          {/* Fare Summary */}
          <div className="w-full bg-surface-hover/70 p-3 rounded-xl border border-border text-xs space-y-1.5">
            <div className="flex justify-between">
              <span className="text-foreground-muted">Standard Fare:</span>
              <span className="font-semibold text-foreground">₹{baseFare}</span>
            </div>
            {smartCardApplied && (
              <div className="flex justify-between text-emerald-600">
                <span>Smart Card 10% Discount:</span>
                <span className="font-bold">-₹{baseFare - discountedFare}</span>
              </div>
            )}
            <div className="border-t border-border pt-1.5 flex justify-between font-extrabold text-sm text-foreground">
              <span>Payable Amount:</span>
              <span className="text-primary tabular-nums">₹{discountedFare}</span>
            </div>
          </div>

          <div className="text-[11px] text-foreground-muted flex items-center gap-1.5">
            <ShieldCheck size={14} className="text-emerald-500" />
            <span>Scan at AFC Automatic Fare Gates before boarding</span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-border bg-surface flex justify-end">
          <button
            onClick={onClose}
            className="w-full py-2.5 rounded-xl bg-primary text-white font-extrabold text-xs hover:bg-primary/90 transition-all cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
