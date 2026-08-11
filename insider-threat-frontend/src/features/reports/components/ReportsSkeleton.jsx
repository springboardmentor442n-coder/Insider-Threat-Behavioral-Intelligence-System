export default function ReportsSkeleton() {

    return (

        <div className="space-y-6 animate-pulse">

            <div className="h-40 rounded-3xl bg-slate-800"/>

            <div className="grid grid-cols-4 gap-5">

                {[...Array(4)].map((_, index)=>(

                    <div

                        key={index}

                        className="h-32 rounded-2xl bg-slate-800"

                    />

                ))}

            </div>

            <div className="h-[500px] rounded-3xl bg-slate-800"/>

        </div>

    );

}
