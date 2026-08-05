import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  User,
  Building2,
  CalendarDays,
  ShieldAlert,
  Cpu,
  Activity,
  FileText,
  Sparkles,
  BrainCircuit,
  ChevronRight,
} from "lucide-react";

import ThreatSeverityBadge from "./ThreatSeverityBadge";

function StatusBadge({ status }) {
  const styles = {
    Open:
      "bg-red-500/20 text-red-400 border border-red-500/30",

    Resolved:
      "bg-green-500/20 text-green-400 border border-green-500/30",

    Investigating:
      "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30",
  };

  return (
    <span
      className={`rounded-full px-4 py-2 text-sm font-semibold ${
        styles[status] ||
        "bg-slate-700 text-white"
      }`}
    >
      {status}
    </span>
  );
}

function RiskCircle({ score }) {
  const percentage = Math.min(score, 100);

  return (
    <div className="relative flex items-center justify-center">

      <svg
        width="170"
        height="170"
        viewBox="0 0 170 170"
      >
        <circle
          cx="85"
          cy="85"
          r="72"
          stroke="#1e293b"
          strokeWidth="10"
          fill="transparent"
        />

        <motion.circle
          cx="85"
          cy="85"
          r="72"
          stroke="#06b6d4"
          strokeWidth="10"
          fill="transparent"
          strokeLinecap="round"
          strokeDasharray={452}
          initial={{
            strokeDashoffset:452,
          }}
          animate={{
            strokeDashoffset:
              452 -
              (452 * percentage) / 100,
          }}
          transition={{
            duration:1,
          }}
          transform="rotate(-90 85 85)"
        />
      </svg>

      <div className="absolute text-center">

        <h1 className="text-5xl font-bold text-cyan-400">
          {score}
        </h1>

        <p className="text-slate-400">
          Risk
        </p>

      </div>

    </div>
  );
}

function DetailCard({
  icon:Icon,
  title,
  value,
}) {
  return (

<div

className="

rounded-2xl

border

border-white/10

bg-white/5

backdrop-blur-xl

p-5

"

>

<div className="flex items-center gap-3">

<Icon
size={18}
className="text-cyan-400"
/>

<p className="text-sm text-slate-400">

{title}

</p>

</div>

<h3 className="mt-4 text-lg font-semibold">

{value||"N/A"}

</h3>

</div>

  );
}

export default function ThreatDetailsDrawer({

open,

threat,

onClose,

onResolve,

onDelete,

}) {

return(

<AnimatePresence>

{open&&threat&&(

<div className="fixed inset-0 z-50 flex justify-end">

<motion.div

initial={{
opacity:0,
}}

animate={{
opacity:1,
}}

exit={{
opacity:0,
}}

className="absolute inset-0 bg-black/70 backdrop-blur-sm"

onClick={onClose}

/>

<motion.div

initial={{
x:700,
}}

animate={{
x:0,
}}

exit={{
x:700,
}}

transition={{
duration:.35,
}}

className="

relative

w-full

max-w-2xl

bg-slate-950/90

backdrop-blur-3xl

border-l

border-cyan-500/20

shadow-[0_0_80px_rgba(6,182,212,.15)]

overflow-y-auto

"

>

<div className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/90 backdrop-blur-xl">

<div className="flex items-center justify-between p-6">

<div>

<h1 className="text-3xl font-bold">

Threat Investigation

</h1>

<p className="text-slate-400">

ID #{threat.id}

</p>

</div>

<button

onClick={onClose}

className="rounded-xl p-2 transition hover:bg-red-500/20"

>

<X/>

</button>

</div>

</div>

<div className="space-y-8 p-8">

<div className="flex justify-center">

<RiskCircle

score={threat.risk_score}

/>

</div>

<div className="grid grid-cols-2 gap-5">

<DetailCard

icon={User}

title="Employee"

value={threat.employee_name}

/>

<DetailCard

icon={Building2}

title="Department"

value={threat.department}

/>

<DetailCard

icon={ShieldAlert}

title="Threat"

value={threat.threat_type}

/>

<DetailCard

icon={CalendarDays}

title="Created"

value={new Date(threat.created_at).toLocaleString()}

/>

</div>

<div>

<h2 className="mb-4 flex items-center gap-2 text-xl font-bold">

<Activity
className="text-cyan-400"/>

Threat Summary

</h2>

<div

className="

rounded-2xl

border

border-white/10

bg-white/5

backdrop-blur-xl

p-6

leading-8

"

>

{threat.description}

</div>

</div>

<div>

<h2 className="mb-4 flex items-center gap-2 text-xl font-bold">

<Cpu
className="text-cyan-400"/>

Evidence

</h2>

<div

className="

rounded-2xl

border

border-white/10

bg-white/5

backdrop-blur-xl

p-6

"

>

{threat.evidence||

"No evidence available"}

</div>

</div>

<div>

<h2 className="mb-4 flex items-center gap-2 text-xl font-bold">

<BrainCircuit
className="text-cyan-400"/>

AI Analysis

</h2>

<div

className="

rounded-2xl

border

border-cyan-500/20

bg-cyan-500/5

backdrop-blur-xl

p-6

"

>

<div className="flex gap-4">

<Sparkles
className="text-cyan-400"/>

<div>

<p>

AI classified this employee as

<strong className="text-cyan-400">

{" "}High Behavioral Risk

</strong>

based on anomaly detection,
login behavior,
file activity,
device usage,
and psychometric profile.

</p>

</div>

</div>

</div>

</div>

<div className="flex items-center justify-between">

<ThreatSeverityBadge

severity={threat.severity}

/>

<StatusBadge

status={threat.status}

/>

</div>

</div>

<div className="sticky bottom-0 border-t border-white/10 bg-slate-950/90 backdrop-blur-xl p-6">

<div className="grid grid-cols-2 gap-4">

<button

onClick={onResolve}

className="

rounded-2xl

bg-green-600

py-4

font-semibold

transition

hover:bg-green-700

"

>

Resolve Threat

</button>

<button

onClick={onDelete}

className="

rounded-2xl

bg-red-600

py-4

font-semibold

transition

hover:bg-red-700

"

>

Delete Threat

</button>

</div>

</div>

</motion.div>

</div>

)}

</AnimatePresence>

);

}
