import { Search, RefreshCcw } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

export default function InvestigationToolbar({
    search,
    setSearch,
}) {

    const queryClient = useQueryClient();

    const handleRefresh = async () => {

        await queryClient.refetchQueries({
            queryKey: ["investigation"],
            type: "active",
        });

    };

    return (

        <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-4">

            <div className="relative">

                <Search
                    size={18}
                    className="absolute left-3 top-3 text-slate-400"
                />

                <input

                    value={search}

                    onChange={(e) =>
                        setSearch(e.target.value)
                    }

                    placeholder="Search investigations..."

                    className="w-80 rounded-xl border border-cyan-500/20 bg-slate-800 py-2 pl-10 pr-4 text-white outline-none"

                />

            </div>

            <button

                onClick={handleRefresh}

                className="flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-2 text-cyan-300 hover:bg-cyan-500/20"

            >

                <RefreshCcw size={18} />

                Refresh

            </button>

        </div>

    );

}
