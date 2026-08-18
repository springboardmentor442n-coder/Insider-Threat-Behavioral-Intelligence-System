import { useState, useEffect } from "react";
import { predictUser } from "../services/api";

function PredictionForm({ setPredictionResult, setIsLoading, isLoading, addRecentAnalysis }) {
    const defaultState = {
        employeeId: "",
        device_connections: "",
        emails_sent: "",
        files_accessed: "",
        websites_visited: "",
        logon_count: "",
        O: "",
        C: "",
        E: "",
        A: "",
        N: "",
    };

    const [formData, setFormData] = useState(defaultState);
    const [validationError, setValidationError] = useState("");
    const [employees, setEmployees] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/employees")
            .then(res => res.json())
            .then(data => setEmployees(data.employees || []))
            .catch(err => console.error("Failed to fetch employees:", err));
    }, []);

    function handleChange(event) {
        const { name, value } = event.target;
        
        let parsedValue = value;
        if (name !== "employeeId" && value !== "") {
            parsedValue = Number(value);
        }

        setFormData({
            ...formData,
            [name]: parsedValue,
        });
        setValidationError("");
    }

    const preventInvalidChars = (e) => {
        if (["e", "E", "+", "-"].includes(e.key)) {
            e.preventDefault();
        }
    };

    async function handleSubmit(event) {
        event.preventDefault();
        setValidationError("");

        // Validation for negative numbers
        const metrics = ["device_connections", "emails_sent", "files_accessed", "websites_visited", "logon_count"];
        for (let metric of metrics) {
            if (formData[metric] !== "" && formData[metric] < 0) {
                setValidationError("Value cannot be negative.");
                return;
            }
        }

        setIsLoading(true);
        setPredictionResult(null);

        try {
            const { employeeId, ...predictData } = formData;
            const result = await predictUser(predictData);
            setPredictionResult(result.prediction);
            
            if (addRecentAnalysis) {
                addRecentAnalysis({
                    id: Math.random().toString(36).substring(7).toUpperCase(),
                    employeeId: employeeId || "Unknown",
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    prediction: result.prediction,
                    riskLevel: result.prediction === "INSIDER" || result.prediction === "Threat" ? "HIGH" : "LOW",
                    activity: {
                        deviceConnections: formData.device_connections,
                        emailsSent: formData.emails_sent,
                        filesAccessed: formData.files_accessed,
                        websitesVisited: formData.websites_visited,
                        logonCount: formData.logon_count
                    },
                    ocean: {
                        openness: formData.O,
                        conscientiousness: formData.C,
                        extraversion: formData.E,
                        agreeableness: formData.A,
                        neuroticism: formData.N
                    },
                    status: "COMPLETED"
                });
            }
        } catch (error) {
            setPredictionResult("ERROR");
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }

    function handleClear() {
        setFormData(defaultState);
        setPredictionResult(null);
        setValidationError("");
    }

    return (
        <form onSubmit={handleSubmit} noValidate>
            {validationError && (
                <div className="login-error" style={{ marginBottom: '1rem' }}>
                    {validationError}
                </div>
            )}
            
            <div className="section-title" style={{ marginTop: 0 }}>BEHAVIORAL ACTIVITY</div>
            <div className="form-section-2col">
                <div className="form-group-detailed" style={{ gridColumn: '1 / -1' }}>
                    <label>EMPLOYEE ID</label>
                    <span className="field-desc">Select an employee for manual analysis</span>
                    <select
                        name="employeeId"
                        value={formData.employeeId}
                        onChange={handleChange}
                        required
                        className="form-control"
                        style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-main)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', borderRadius: '4px', fontSize: '1rem', marginTop: '0.5rem' }}
                    >
                        <option value="" disabled>Select Employee</option>
                        {employees.map(emp => (
                            <option key={emp} value={emp}>{emp}</option>
                        ))}
                    </select>
                </div>
                <div className="form-group-detailed">
                    <label>DEVICE CONNECTIONS</label>
                    <span className="field-desc">Number of device connection events</span>
                    <input
                        type="number"
                        min="0"
                        name="device_connections"
                        placeholder="e.g. 750"
                        value={formData.device_connections}
                        onChange={handleChange}
                        onKeyDown={preventInvalidChars}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>EMAILS SENT</label>
                    <span className="field-desc">Number of emails sent</span>
                    <input
                        type="number"
                        min="0"
                        name="emails_sent"
                        placeholder="e.g. 300"
                        value={formData.emails_sent}
                        onChange={handleChange}
                        onKeyDown={preventInvalidChars}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>FILES ACCESSED</label>
                    <span className="field-desc">Number of files accessed</span>
                    <input
                        type="number"
                        min="0"
                        name="files_accessed"
                        placeholder="e.g. 1000"
                        value={formData.files_accessed}
                        onChange={handleChange}
                        onKeyDown={preventInvalidChars}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>WEBSITES VISITED</label>
                    <span className="field-desc">Number of websites visited</span>
                    <input
                        type="number"
                        min="0"
                        name="websites_visited"
                        placeholder="e.g. 30000"
                        value={formData.websites_visited}
                        onChange={handleChange}
                        onKeyDown={preventInvalidChars}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>LOGON COUNT</label>
                    <span className="field-desc">Number of login events</span>
                    <input
                        type="number"
                        min="0"
                        name="logon_count"
                        placeholder="e.g. 900"
                        value={formData.logon_count}
                        onChange={handleChange}
                        onKeyDown={preventInvalidChars}
                        required
                    />
                </div>
            </div>

            <div className="section-title">PSYCHOMETRIC PROFILE (OCEAN)</div>
            <div className="form-section-2col">
                <div className="form-group-detailed">
                    <label>OPENNESS (O)</label>
                    <span className="field-desc">Score 10 to 50</span>
                    <input
                        type="number"
                        min="0"
                        name="O"
                        placeholder="e.g. 35"
                        value={formData.O}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>CONSCIENTIOUSNESS (C)</label>
                    <span className="field-desc">Score 10 to 50</span>
                    <input
                        type="number"
                        min="0"
                        name="C"
                        placeholder="e.g. 35"
                        value={formData.C}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>EXTRAVERSION (E)</label>
                    <span className="field-desc">Score 10 to 50</span>
                    <input
                        type="number"
                        min="0"
                        name="E"
                        placeholder="e.g. 25"
                        value={formData.E}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>AGREEABLENESS (A)</label>
                    <span className="field-desc">Score 10 to 50</span>
                    <input
                        type="number"
                        min="0"
                        name="A"
                        placeholder="e.g. 30"
                        value={formData.A}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group-detailed">
                    <label>NEUROTICISM (N)</label>
                    <span className="field-desc">Score 10 to 50</span>
                    <input
                        type="number"
                        min="0"
                        name="N"
                        placeholder="e.g. 30"
                        value={formData.N}
                        onChange={handleChange}
                        required
                    />
                </div>
            </div>

            <div className="form-actions-group">
                <button type="submit" className="submit-btn" disabled={isLoading}>
                    {isLoading ? "ANALYZING..." : "ANALYZE BEHAVIOR"}
                </button>
                <button type="button" className="clear-btn" onClick={handleClear} disabled={isLoading}>
                    CLEAR FORM
                </button>
            </div>
        </form>
    );
}

export default PredictionForm;