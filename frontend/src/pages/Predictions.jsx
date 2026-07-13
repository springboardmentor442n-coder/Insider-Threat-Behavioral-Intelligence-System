import Sidebar from "../components/Sidebar";

function Predictions() {
  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <Sidebar />

      <div style={{ flex: 1, padding: "40px", color: "white" }}>
        <h1>Threat Predictions</h1>

        <div
          style={{
            marginTop: "30px",
            padding: "30px",
            background: "#1e293b",
            borderRadius: "12px",
          }}
        >
          <h2>No Predictions Available</h2>
          <p>AI prediction module will be integrated in Milestone 2.</p>
        </div>
      </div>
    </div>
  );
}

export default Predictions;