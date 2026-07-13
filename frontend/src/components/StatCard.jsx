import "./../styles/StatCard.css";

function StatCard({ title, value, color }) {
  return (
    <div className="stat-card">
      <h3>{title}</h3>
      <h1 style={{ color }}>{value}</h1>
    </div>
  );
}

export default StatCard;