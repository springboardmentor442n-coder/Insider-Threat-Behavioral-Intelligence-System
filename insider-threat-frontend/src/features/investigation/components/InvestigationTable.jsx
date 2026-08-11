export default function InvestigationTable({

    cases,

    onSelect,

}) {

    return (

        <div className="overflow-hidden rounded-2xl border border-cyan-500/20 bg-slate-900/70">

            <table className="w-full">

                <thead className="bg-slate-800">

                    <tr>

                        <th className="p-4 text-left">Case</th>
                        <th className="p-4 text-left">Employee</th>
                        <th className="p-4 text-left">Department</th>
                        <th className="p-4 text-left">Risk</th>
                        <th className="p-4 text-left">Status</th>

                    </tr>

                </thead>

                <tbody>

                    {cases.map((item) => (

                        <tr

                            key={item.id}

                            onClick={() => onSelect(item)}

                            className="cursor-pointer border-t border-slate-800 hover:bg-slate-800/50"

                        >

                            <td className="p-4">

                                {item.id}

                            </td>

                            <td className="p-4">

                                {item.employee}

                            </td>

                            <td className="p-4">

                                {item.department}

                            </td>

                            <td className="p-4 text-red-400 font-semibold">

                                {item.risk_score}

                            </td>

                            <td className="p-4">

                                {item.status}

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}
