import { useState } from "react";
import { useNavigate } from "react-router-dom";
import authService from "../../services/auth/authService";

export default function LoginPage() {

  const navigate = useNavigate();

  const [username, setUsername] = useState("nandan");
  const [password, setPassword] = useState("Nandan@40123");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {

    e.preventDefault();

    try {

      setLoading(true);

      await authService.login(
        username,
        password
      );

      navigate("/");

    } catch (err) {

      alert(
        err.response?.data?.detail ??
        "Login Failed"
      );

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="min-h-screen flex items-center justify-center bg-slate-950">

      <form
        onSubmit={handleLogin}
        className="bg-slate-900 p-8 rounded-xl w-96 space-y-5"
      >

        <h1 className="text-3xl font-bold text-white">
          SentinelAI Login
        </h1>

        <input
          className="w-full rounded bg-slate-800 p-3 text-white"
          value={username}
          onChange={(e)=>setUsername(e.target.value)}
        />

        <input
          type="password"
          className="w-full rounded bg-slate-800 p-3 text-white"
          value={password}
          onChange={(e)=>setPassword(e.target.value)}
        />

        <button
          className="w-full rounded bg-cyan-500 py-3 font-bold"
        >
          {loading ? "Signing In..." : "Login"}
        </button>

      </form>

    </div>

  );

}
