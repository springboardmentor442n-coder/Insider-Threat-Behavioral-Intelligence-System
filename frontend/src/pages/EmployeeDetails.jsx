import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

export default function EmployeeDetails() {

    const { employee_id } = useParams();

    const [data, setData] = useState(null);

    useEffect(() => {
        loadEmployee();
    }, []);

    async function loadEmployee() {

        try {

            const res = await axios.get(
                `http://127.0.0.1:8000/behavior/${employee_id}`
            );

            setData(res.data);

        } catch (err) {

            console.log(err);

        }

    }

    if (!data)
        return <h2>Loading...</h2>;

    return (

        <div className="container">

            <h2>Employee Details</h2>

            <br />

            <table>

                <tbody>

                    <tr>

                        <td><b>Employee ID</b></td>

                        <td>{data.employee.employee_id}</td>

                    </tr>

                    <tr>

                        <td><b>Name</b></td>

                        <td>{data.employee.name}</td>

                    </tr>

                    <tr>

                        <td><b>Department</b></td>

                        <td>{data.employee.department}</td>

                    </tr>

                    <tr>

                        <td><b>Designation</b></td>

                        <td>{data.employee.designation}</td>

                    </tr>

                    <tr>

                        <td><b>Email</b></td>

                        <td>{data.employee.email}</td>

                    </tr>

                    <tr>

                        <td><b>Total Predictions</b></td>

                        <td>{data.total_predictions}</td>

                    </tr>

                    <tr>

                        <td><b>High Risk Events</b></td>

                        <td>{data.high_risk}</td>

                    </tr>

                </tbody>

            </table>

            <br />

            <h3>Prediction History</h3>

            <table>

                <thead>

                    <tr>

                        <th>Login Count</th>

                        <th>Devices</th>

                        <th>Hour</th>

                        <th>Weekend</th>

                        <th>Risk</th>

                        <th>Confidence</th>

                    </tr>

                </thead>

                <tbody>

                    {

                        data.predictions.map((p) => (

                            <tr key={p.id}>

                                <td>{p.login_count}</td>

                                <td>{p.unique_pc_count}</td>

                                <td>{p.hour}</td>

                                <td>

                                    {p.is_weekend ? "Yes" : "No"}

                                </td>

                                <td>

                                    <span
                                        style={{

                                            color:
                                                p.risk_level === "HIGH"
                                                    ? "red"
                                                    : "green",

                                            fontWeight: "bold"

                                        }}
                                    >

                                        {p.risk_level}

                                    </span>

                                </td>

                                <td>{p.confidence}%</td>

                            </tr>

                        ))

                    }

                </tbody>

            </table>

        </div>

    );

}