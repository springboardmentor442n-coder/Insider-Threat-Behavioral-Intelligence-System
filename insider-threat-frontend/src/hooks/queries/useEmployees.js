import { useQuery } from "@tanstack/react-query";
import employeeService from "../../services/api/employeeService";

export function useEmployees() {

    return useQuery({

        queryKey:["employees"],

        queryFn: employeeService.getAllEmployees

    });

}
