import GlassCard from "../ui/GlassCard";

const systems = [
  { name: "Backend API", status: "Online" },
  { name: "AI Engine", status: "Healthy" },
  { name: "Database", status: "Connected" },
  { name: "Detection Model", status: "Running" },
];

export default function SystemStatus() {
  return (
    <GlassCard className="p-6">
      <h2 className="text-xl font-bold">
        System Status
      </h2>

      <div className="mt-6 space-y-4">
        {systems.map((item) => (
          <div
            key={item.name}
            className="flex items-center justify-between"
          >
            <span className="text-slate-400">
              {item.name}
            </span>

            <span className="font-semibold text-green-400">
              {item.status}
            </span>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
