import { useQuery } from "@tanstack/react-query";
import {
  Clock,
  FileWarning,
  LogIn,
  UploadCloud,
  DownloadCloud,
  ShieldAlert,
  Loader2,
} from "lucide-react";
import api from "../../../lib/axios";

const ACTIVITY_ENDPOINT = "/activity";

const EVENT_ICONS = {
  login: LogIn,
  file_upload: UploadCloud,
  file_download: DownloadCloud,
  policy_violation: FileWarning,
  risk_flag: ShieldAlert,
  default: Clock,
};

function useEmployeeActivity(employeeId) {
  return useQuery({
    queryKey: ["employees", employeeId, "activity"],

    queryFn: async () => {
      const { data } = await api.get(ACTIVITY_ENDPOINT, {
        params: {
          employee_id: employeeId,
        },
      });

      if (Array.isArray(data)) {
        return data;
      }

      return data?.items ?? [];
    },

    enabled: Boolean(employeeId),

    staleTime: 30000,
  });
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "-";

  try {
    return new Date(timestamp).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return timestamp;
  }
}

export default function EmployeeActivityTimeline({ employeeId }) {
  const {
    data: events = [],
    isLoading,
    isError,
  } = useEmployeeActivity(employeeId);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 py-8 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading activity...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-400">
        Unable to load employee activity.
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-800 p-6 text-center text-sm text-slate-500">
        No activity available.
      </div>
    );
  }

  return (
    <ol className="relative ml-3 border-l border-slate-800 pl-5 space-y-5">
      {events.map((event, index) => {
        const Icon =
          EVENT_ICONS[event.event_type] || EVENT_ICONS.default;

        const flagged =
          event.event_type === "policy_violation" ||
          event.event_type === "risk_flag";

        return (
          <li
            key={event.id ?? index}
            className="relative"
          >
            <span
              className={`absolute -left-[27px] flex h-5 w-5 items-center justify-center rounded-full ring-4 ring-slate-950 ${
                flagged
                  ? "bg-red-500/20 text-red-400"
                  : "bg-cyan-500/20 text-cyan-400"
              }`}
            >
              <Icon className="h-3 w-3" />
            </span>

            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium text-slate-200">
                {event.title ||
                  event.event_type?.replaceAll("_", " ") ||
                  "Activity"}
              </p>

              <span className="text-xs text-slate-500 whitespace-nowrap">
                {formatTimestamp(
                  event.timestamp || event.created_at
                )}
              </span>
            </div>

            {event.description && (
              <p className="mt-1 text-xs text-slate-500">
                {event.description}
              </p>
            )}
          </li>
        );
      })}
    </ol>
  );
}
