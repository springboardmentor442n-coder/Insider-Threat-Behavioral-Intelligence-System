function ResultCard({ result, isLoading }) {
    if (isLoading) {
        return (
            <div className="result-card">
                <div className="result-empty">
                    <svg className="result-icon-empty" style={{ animation: "pulse 1.5s infinite" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <p className="ready-title">ANALYZING BEHAVIOR...</p>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="result-card">
                <div className="result-empty">
                    <svg className="result-icon-empty" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="ready-title">READY FOR ANALYSIS</p>
                    <p className="ready-desc">Enter employee activity metrics and run the analysis.</p>
                </div>
            </div>
        );
    }

    const isThreat = result === "ANOMALY" || result === "Threat";

    return (
        <div className="result-card">
            <div className="result-section-header">RISK ASSESSMENT</div>
            
            <div className="result-content-structured">
                <div className="result-data-row">
                    <span className="result-data-label">Model Result</span>
                    <span className="result-data-value">{result}</span>
                </div>
                <div className="result-data-row">
                    <span className="result-data-label">Risk Level</span>
                    <div className={`status-badge ${isThreat ? 'insider' : 'normal'}`}>
                        {isThreat ? (
                            <>
                                <svg className="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                HIGH RISK - ANOMALY DETECTED
                            </>
                        ) : (
                            <>
                                <svg className="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                BEHAVIOR NORMAL
                            </>
                        )}
                    </div>
                </div>

                <div className="result-message-box">
                    {isThreat 
                        ? "Warning: Anomalous behavioral patterns detected. The model indicates a high risk of abnormal activity. Immediate review of this user's activities is recommended."
                        : "Behavioral metrics are within normal parameters. No significant anomalous activity detected."
                    }
                </div>
            </div>
        </div>
    );
}

export default ResultCard;
