import { motion } from "framer-motion";
import ThreatSeverityBadge from "./ThreatSeverityBadge";

function EmployeeAvatar({ name }) {
  const initials = name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .substring(0, 2);

  return (
    <div
      className="
        flex

        h-12
        w-12

        items-center
        justify-center

        rounded-full

        bg-gradient-to-br

        from-cyan-500

        to-blue-600

        font-bold

        text-white

        shadow-lg
      "
    >
      {initials}
    </div>
  );
}

function StatusBadge({ status }) {

  let style =
    "bg-slate-700 text-slate-200";

  if (status === "Open")
    style =
      "bg-red-500/20 text-red-400 border border-red-500/30";

  if (status === "Resolved")
    style =
      "bg-green-500/20 text-green-400 border border-green-500/30";

  if (status === "Investigating")
    style =
      "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30";

  return (
    <span
      className={`
        rounded-full
        px-4
        py-1
        text-xs
        font-semibold
        ${style}
      `}
    >
      {status}
    </span>
  );
}

function RiskBar({ score }) {

  let color = "bg-green-500";

  if (score >= 90)
    color = "bg-red-500";

  else if (score >= 75)
    color = "bg-orange-500";

  else if (score >= 50)
    color = "bg-yellow-400";

  return (
    <div className="w-40">

      <div className="flex justify-between">

        <span className="font-bold">
          {score}
        </span>

        <span className="text-xs text-slate-400">
          %
        </span>

      </div>

      <div
        className="
          mt-2

          h-2

          rounded-full

          bg-slate-700
        "
      >

        <motion.div

          initial={{
            width:0,
          }}

          animate={{
            width:`${score}%`,
          }}

          transition={{
            duration:1,
          }}

          className={`

            h-2

            rounded-full

            ${color}

          `}
        />

      </div>

    </div>
  );
}

export default function ThreatRow({

  threat,

  onClick,

}) {

  return (

<tr

onClick={()=>onClick(threat)}

className="

cursor-pointer

border-b

border-white/5

transition-all

duration-300

hover:bg-cyan-500/10

hover:backdrop-blur-xl

"

>

<td className="px-6 py-5">

<div className="flex items-center gap-4">

<EmployeeAvatar

name={threat.employee_name}

/>

<div>

<h3 className="font-semibold">

{threat.employee_name}

</h3>

<p className="text-sm text-slate-400">

ID #{threat.employee_id}

</p>

</div>

</div>

</td>

<td className="px-6">

{threat.department}

</td>

<td className="px-6">

<div>

<p className="font-semibold">

{threat.threat_type}

</p>

<p className="text-sm text-slate-400 line-clamp-1">

{threat.description}

</p>

</div>

</td>

<td className="px-6">

<RiskBar

score={threat.risk_score}

/>

</td>

<td className="px-6 text-center">

<ThreatSeverityBadge

severity={threat.severity}

/>

</td>

<td className="px-6 text-center">

<StatusBadge

status={threat.status}

/>

</td>

<td className="px-6 text-center whitespace-nowrap">

{new Date(

threat.created_at

).toLocaleDateString()}

</td>

</tr>

  );

}
