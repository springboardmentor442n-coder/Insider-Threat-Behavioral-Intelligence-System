import Sidebar from "./Sidebar";

export default function Layout({ title, children }) {
  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0f172a",
      }}
    >
      <Sidebar />

      <div
        style={{
          flex: 1,
          padding: "35px",
          color: "white",
          overflowY: "auto",
        }}
      >
        <h1
          style={{
            marginBottom: "25px",
            fontSize: "32px",
          }}
        >
          {title}
        </h1>

        {children}
      </div>
    </div>
  );
}