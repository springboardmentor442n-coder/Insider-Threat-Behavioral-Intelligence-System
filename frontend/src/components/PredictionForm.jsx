import { useState } from "react";
import { predictUser } from "../services/api";

function PredictionForm({ setPredictionResult, setIsLoading, isLoading }) {
    const [formData, setFormData] = useState({
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
    });

    function handleChange(event) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value === "" ? "" : Number(event.target.value),
        });
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setIsLoading(true);
        setPredictionResult(null);

        try {
            const result = await predictUser(formData);
            setPredictionResult(result.prediction);
        } catch (error) {
            setPredictionResult("ERROR");
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="section-title">Activity Metrics</div>
            <div className="form-section">
                <div className="form-group">
                    <label>Device Connections</label>
                    <input
                        type="number"
                        name="device_connections"
                        placeholder="e.g. 5"
                        value={formData.device_connections}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Emails Sent</label>
                    <input
                        type="number"
                        name="emails_sent"
                        placeholder="e.g. 120"
                        value={formData.emails_sent}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Files Accessed</label>
                    <input
                        type="number"
                        name="files_accessed"
                        placeholder="e.g. 45"
                        value={formData.files_accessed}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Websites Visited</label>
                    <input
                        type="number"
                        name="websites_visited"
                        placeholder="e.g. 30"
                        value={formData.websites_visited}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Logon Count</label>
                    <input
                        type="number"
                        name="logon_count"
                        placeholder="e.g. 3"
                        value={formData.logon_count}
                        onChange={handleChange}
                        required
                    />
                </div>
            </div>

            <div className="section-title">Psychometric Profile (OCEAN)</div>
            <div className="form-section">
                <div className="form-group">
                    <label>Openness (O)</label>
                    <input
                        type="number"
                        step="0.1"
                        name="O"
                        placeholder="Score 0-5"
                        value={formData.O}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Conscientiousness (C)</label>
                    <input
                        type="number"
                        step="0.1"
                        name="C"
                        placeholder="Score 0-5"
                        value={formData.C}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Extraversion (E)</label>
                    <input
                        type="number"
                        step="0.1"
                        name="E"
                        placeholder="Score 0-5"
                        value={formData.E}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Agreeableness (A)</label>
                    <input
                        type="number"
                        step="0.1"
                        name="A"
                        placeholder="Score 0-5"
                        value={formData.A}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label>Neuroticism (N)</label>
                    <input
                        type="number"
                        step="0.1"
                        name="N"
                        placeholder="Score 0-5"
                        value={formData.N}
                        onChange={handleChange}
                        required
                    />
                </div>
            </div>

            <button type="submit" className="submit-btn" disabled={isLoading}>
                {isLoading ? "Analyzing Profile..." : "Run Behavioral Analysis"}
            </button>
        </form>
    );
}

export default PredictionForm;