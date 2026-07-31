import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Eye,
  EyeOff,
  Shield,
  Lock,
  User,
  ArrowLeft,
} from "lucide-react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {

  const savedUser = localStorage.getItem("rememberUser");

  if (savedUser) {

    setUsername(savedUser);
    setRememberMe(true);

  }

}, []);

  const login = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError("");

      const response = await axios.post(
        "http://127.0.0.1:8000/login",
        {
          username,
          password,
        }
      );

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      localStorage.setItem(
        "username",
        username
      );

      if (rememberMe) {
        localStorage.setItem("rememberUser", username);
      } else {
        localStorage.removeItem("rememberUser");
      }

      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950">

      {/* Background */}

      <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900"></div>

      <div className="absolute left-0 top-0 h-96 w-96 rounded-full bg-cyan-500/20 blur-3xl animate-pulse"></div>

      <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl animate-pulse"></div>

      {/* Back Button */}

      <Link
        to="/"
        className="absolute left-8 top-8 z-20 flex items-center gap-2 rounded-xl border border-cyan-500/30 bg-slate-900/60 px-4 py-2 text-cyan-400 backdrop-blur hover:bg-cyan-500/10"
      >
        <ArrowLeft size={18} />
        Back to Home
      </Link>

      {/* Login Card */}

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 w-full max-w-md rounded-3xl border border-white/10 bg-white/10 p-10 shadow-2xl backdrop-blur-xl"
      >

        <div className="mb-8 flex justify-center">

          <div className="rounded-full bg-cyan-500 p-5">

            <Shield size={45} color="white" />

          </div>

        </div>

        <h1 className="mb-2 text-center text-3xl font-bold text-white">
          Welcome Back
        </h1>

        <p className="mb-8 text-center text-slate-300">
          AI Insider Threat Detection Platform
        </p>

        <form onSubmit={login} className="space-y-6">
                    {/* Username */}

          <div className="relative">

            <User
              className="absolute left-4 top-4 text-slate-400"
              size={20}
            />

            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full rounded-xl border border-white/10 bg-slate-900/50 py-4 pl-12 pr-4 text-white outline-none transition focus:border-cyan-400"
            />

          </div>

          {/* Password */}

          <div className="relative">

            <Lock
              className="absolute left-4 top-4 text-slate-400"
              size={20}
            />

            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-xl border border-white/10 bg-slate-900/50 py-4 pl-12 pr-12 text-white outline-none transition focus:border-cyan-400"
            />

            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white transition"
            >
              {showPassword ? (
                <EyeOff size={20} />
              ) : (
                <Eye size={20} />
              )}
            </button>

          </div>

          {/* Remember + Forgot */}

          <div className="flex items-center justify-between">

            <label className="flex items-center gap-2 text-sm text-slate-300">

              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-slate-600 accent-cyan-500"
              />

              Remember me

            </label>

            <button
              type="button"
              onClick={() =>
                alert(
                  "Password reset functionality will be available in a future update."
                )
              }
              className="text-sm text-cyan-400 transition hover:text-cyan-300"
            >
              Forgot Password?
            </button>

          </div>

          {/* Error */}

          {error && (

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-center text-red-300"
            >
              {error}
            </motion.div>

          )}

          {/* Login Button */}

          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            disabled={loading}
            className="flex w-full items-center justify-center rounded-xl bg-cyan-500 py-4 text-lg font-bold text-white transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? (

              <>
                <svg
                  className="mr-3 h-5 w-5 animate-spin"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    opacity="0.25"
                  />

                  <path
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  />
                </svg>

                Signing In...

              </>

            ) : (

              "Login"

            )}

          </motion.button>

        </form>

        <div className="mt-8 border-t border-white/10 pt-5 text-center">

          <p className="text-sm text-slate-400">

            Secure access to the AI Insider Threat Detection Platform

          </p>

        </div>

      </motion.div>

    </div>

  );

}