import { ShieldCheck } from "lucide-react";
import PageHeader from "../shared/PageHeader";

export default function HeroBanner() {
  return (
    <PageHeader
      icon={ShieldCheck}
      title="Security Operations Overview"
      subtitle="Real-time behavioral intelligence across the enterprise • CERT Dataset Baseline"
      badge={
        <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Active Intelligence
        </span>
      }
    >
      <div className="flex items-center gap-2">
        <span className="rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold text-cyan-300">
          7-Model Ensemble
        </span>
        <span className="rounded-xl border border-blue-500/20 bg-blue-500/10 px-3 py-1.5 text-xs font-semibold text-blue-300">
          1,000 Employees Evaluated
        </span>
      </div>
    </PageHeader>
  );
}
