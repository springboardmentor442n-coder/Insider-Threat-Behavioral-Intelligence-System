import {
    Search,
} from "lucide-react";

export default function ReportsToolbar({
    search,
    setSearch,
}) {
    return (
        <div className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-3
            rounded-2xl
            border
            border-cyan-500/15
            bg-slate-900/65
            p-3
        ">
            <div className="relative">
                <Search
                    className="
                        absolute
                        left-3
                        top-2.5
                        text-slate-500
                    "
                    size={17}
                />

                <input
                    value={search}
                    onChange={(event) =>
                        setSearch(
                            event.target.value
                        )
                    }
                    placeholder="Search reports..."
                    className="
                        w-64
                        rounded-xl
                        border
                        border-cyan-500/15
                        bg-slate-950/40
                        py-2
                        pl-9
                        pr-3
                        text-sm
                        text-white
                        outline-none
                        placeholder:text-slate-600
                        focus:border-cyan-500/30
                    "
                />
            </div>

            <p className="text-xs text-slate-500">
                Live reports are generated from
                current backend data.
            </p>
        </div>
    );
}
