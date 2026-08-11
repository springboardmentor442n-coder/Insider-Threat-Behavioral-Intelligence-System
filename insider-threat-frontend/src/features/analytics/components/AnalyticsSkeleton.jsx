export default function AnalyticsSkeleton() {

    return (

        <div className="grid grid-cols-4 gap-6">

            {[...Array(8)].map((_, index) => (

                <div

                    key={index}

                    className="h-36 rounded-3xl bg-slate-800 animate-pulse"

                />

            ))}

        </div>

    );

}
