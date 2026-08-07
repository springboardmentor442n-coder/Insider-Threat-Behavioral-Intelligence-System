import { useState } from "react";
import PredictionForm from "./components/PredictionForm";
import ResultCard from "./components/ResultCard";

function App() {
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Behavioral Intelligence Dashboard</h1>
        <p>Insider Threat Early Warning System</p>
      </header>
      
      <main className="dashboard-grid">
        <div className="card">
          <h2>Analyze User Behavior</h2>
          <PredictionForm 
            setPredictionResult={setPredictionResult} 
            setIsLoading={setIsLoading} 
            isLoading={isLoading} 
          />
        </div>
        
        <div className="card">
          <h2>Analysis Result</h2>
          <ResultCard 
            result={predictionResult} 
            isLoading={isLoading} 
          />
        </div>
      </main>
    </div>
  );
}

export default App;