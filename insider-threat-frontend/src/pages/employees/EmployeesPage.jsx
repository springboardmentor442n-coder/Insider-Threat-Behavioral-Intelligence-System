import { useEmployees } from "../../hooks/queries/useEmployees";

export default function EmployeesPage(){

    const {

        data=[],
        isLoading,
        isError

    } = useEmployees();

    if(isLoading)
        return <h1>Loading Employees...</h1>;

    if(isError)
        return <h1>Unable to load employees.</h1>;

    return(

        <div className="space-y-6">

            <h1 className="text-3xl font-bold">
                Employees
            </h1>

            <pre className="bg-slate-900 p-6 rounded-xl overflow-auto">

                {JSON.stringify(data,null,2)}

            </pre>

        </div>

    );

}
