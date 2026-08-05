import GlassCard from "../ui/GlassCard";

export default function InvestigationQueue({
  employees = [],
}) {
  return (
    <GlassCard className="p-6">

      <div className="flex justify-between mb-6">

        <h2 className="text-2xl font-bold">
          Investigation Queue
        </h2>

        <span className="text-cyan-400">
          {employees.length} Pending
        </span>

      </div>

      <div className="space-y-4">

        {employees.slice(0,5).map((emp)=>{

          return(

            <div
              key={emp.user}
              className="
              rounded-2xl

              border
              border-cyan-500/20

              bg-white/5

              p-5

              hover:bg-cyan-500/10

              transition
            "
            >

              <div className="flex justify-between">

                <div>

                  <h3 className="font-semibold text-lg">
                    {emp.employee_name}
                  </h3>

                  <p className="text-slate-400">
                    {emp.department}
                  </p>

                </div>

                <span className="text-cyan-400 font-bold">
                  {emp.risk_score}
                </span>

              </div>

              <div className="mt-5">

                <div className="h-2 rounded-full bg-slate-700">

                  <div
                    className="h-2 rounded-full bg-cyan-400"
                    style={{
                      width:`${emp.risk_score}%`
                    }}
                  />

                </div>

              </div>

            </div>

          )

        })}

      </div>

    </GlassCard>
  );
}
