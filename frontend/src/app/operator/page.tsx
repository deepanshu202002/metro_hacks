import InsightsDashboard from "@/components/InsightsDashboard";

export default function OperatorPage() {
  return (
    <div className="h-screen bg-background text-foreground flex flex-col">
      <div className="bg-surface border-b border-border p-4 flex items-center gap-3">
        <h1 className="text-xl font-black text-primary uppercase tracking-wider">
          One Journey | Metro Operator Control Center
        </h1>
      </div>
      <div className="flex-1 overflow-hidden">
        <InsightsDashboard role="operator" />
      </div>
    </div>
  );
}
