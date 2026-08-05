import GlassCard from "../ui/GlassCard";
import { Clock3 } from "lucide-react";

const events = [
  {
    time: "22:41",
    title: "USB Device Connected",
    employee: "EMP-143",
  },
  {
    time: "22:18",
    title: "Large File Download",
    employee: "EMP-031",
  },
  {
    time: "21:55",
    title: "Abnormal Login",
    employee: "EMP-076",
  },
  {
    time: "21:32",
    title: "Email Anomaly",
    employee: "EMP-104",
  },
];

export default function ActivityFeed() {
  return (
    <GlassCard className="p-6">
      <h2 className="text-xl font-bold">
        Live Activity Feed
      </h2>

      <div className="mt-6 space-y-5">
        {events.map((event) => (
          <div
            key={`${event.time}-${event.employee}`}
            className="flex gap-4"
          >
            <Clock3 className="text-cyan-400 mt-1" size={18} />

            <div>
              <p className="font-semibold">
                {event.title}
              </p>

              <p className="text-slate-400">
                {event.employee}
              </p>

              <p className="text-xs text-slate-500">
                {event.time}
              </p>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
