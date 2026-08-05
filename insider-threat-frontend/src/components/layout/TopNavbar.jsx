import {
  Search,
  Bell,
  Moon,
  Sun,
} from "lucide-react";

export default function TopNavbar() {
  return (
    <header
      className="
      glass-card
      mx-6
      mt-5
      mb-6

      h-20

      rounded-3xl

      flex
      items-center
      justify-between

      px-8
    "
    >
      {/* Search */}

      <div className="relative w-[420px]">

        <Search
          size={18}
          className="
          absolute
          left-5
          top-1/2
          -translate-y-1/2
          text-slate-400
        "
        />

        <input
          type="text"
          placeholder="Search employees, threats, reports..."
          className="
          w-full

          rounded-2xl

          bg-slate-900/40

          border
          border-slate-700

          pl-14
          pr-5
          py-3

          outline-none

          focus:border-cyan-500
        "
        />

      </div>

      {/* Right */}

      <div className="flex items-center gap-5">

        <button
          className="
          relative

          h-12
          w-12

          rounded-2xl

          bg-slate-900/40

          flex
          items-center
          justify-center
        "
        >

          <Bell />

          <span
            className="
            absolute
            top-2
            right-2

            h-2.5
            w-2.5

            rounded-full

            bg-red-500
          "
          />

        </button>

        <button
          className="
          h-12
          w-12

          rounded-2xl

          bg-slate-900/40

          flex
          items-center
          justify-center
        "
        >
          <Moon />
        </button>

        <div
          className="
          flex
          items-center
          gap-4

          rounded-2xl

          bg-slate-900/40

          px-4
          py-2
        "
        >

          <div
            className="
            h-12
            w-12

            rounded-full

            bg-gradient-to-r
            from-cyan-500
            to-blue-600

            flex
            items-center
            justify-center

            font-bold
          "
          >
            N
          </div>

          <div>

            <p className="font-semibold">
              Nandan
            </p>

            <p className="text-xs text-slate-400">
              Security Analyst
            </p>

          </div>

        </div>

      </div>

    </header>
  );
}
