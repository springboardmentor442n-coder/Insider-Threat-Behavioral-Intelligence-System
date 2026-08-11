import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  Shield,
  Eye,
  EyeOff,
  LockKeyhole,
  User,
  ArrowRight,
  AlertCircle,
  Loader2,
} from "lucide-react";

import { useAuth } from "../../providers/AuthProvider";

export default function LoginPage() {
  const navigate = useNavigate();

  const { login } = useAuth();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const [showPassword, setShowPassword] =
    useState(false);

  const [rememberMe, setRememberMe] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  // ============================================================
  // Handle input changes
  // ============================================================

  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    if (error) {
      setError("");
    }
  };

  // ============================================================
  // Login
  // ============================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!formData.username.trim()) {
      setError(
        "Please enter your username."
      );
      return;
    }

    if (!formData.password) {
      setError(
        "Please enter your password."
      );
      return;
    }

    try {
      setLoading(true);

      /*
       * IMPORTANT:
       *
       * Use AuthProvider.login().
       *
       * It:
       * 1. Calls /auth/login
       * 2. Stores the JWT
       * 3. Calls /auth/me
       * 4. Updates AuthProvider.user
       */
      await login(
        formData.username.trim(),
        formData.password
      );

      if (rememberMe) {
        localStorage.setItem(
          "remember_me",
          "true"
        );
      } else {
        localStorage.removeItem(
          "remember_me"
        );
      }

      /*
       * "/" is the protected dashboard route.
       */
      navigate("/", {
        replace: true,
      });
    } catch (err) {
      console.error(
        "Login failed:",
        err
      );

      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to sign in. Please check your username and password.";

      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">

      <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">

        {/* Background */}
        <div className="pointer-events-none absolute inset-0">

          <div className="absolute left-1/2 top-1/2 h-[520px] w-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-[120px]" />

          <div className="absolute left-[10%] top-[15%] h-48 w-48 rounded-full bg-blue-600/10 blur-[90px]" />

          <div className="absolute bottom-[10%] right-[10%] h-56 w-56 rounded-full bg-cyan-400/10 blur-[100px]" />

        </div>

        {/* Grid */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(148,163,184,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.5) 1px, transparent 1px)",
            backgroundSize:
              "40px 40px",
          }}
        />

        {/* Main */}
        <div className="relative z-10 w-full max-w-md">

          {/* Branding */}
          <div className="mb-8 text-center">

            <div className="mb-5 flex justify-center">

              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-sky-500 to-blue-600 shadow-xl shadow-cyan-500/20">

                <Shield className="h-8 w-8 text-white" />

              </div>

            </div>

            <h1 className="text-3xl font-bold tracking-tight">
              SentinelAI
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Insider Threat Behavioral Intelligence
            </p>

          </div>

          {/* Card */}
          <div className="rounded-3xl border border-slate-800/80 bg-slate-900/80 p-7 shadow-2xl shadow-black/30 backdrop-blur-xl sm:p-8">

            <div className="mb-7">

              <h2 className="text-2xl font-semibold text-white">
                Welcome back
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                Sign in to access your security intelligence dashboard.
              </p>

            </div>

            {/* Error */}
            {error && (
              <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3">

                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />

                <p className="text-sm leading-5 text-red-300">
                  {error}
                </p>

              </div>
            )}

            {/* Form */}
            <form
              onSubmit={handleSubmit}
              className="space-y-5"
            >

              {/* Username */}
              <div>

                <label
                  htmlFor="username"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Username
                </label>

                <div className="relative">

                  <User className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />

                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    disabled={loading}
                    className="h-12 w-full rounded-xl border border-slate-700 bg-slate-800/80 pl-12 pr-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                  />

                </div>

              </div>

              {/* Password */}
              <div>

                <div className="mb-2 flex items-center justify-between">

                  <label
                    htmlFor="password"
                    className="text-sm font-medium text-slate-300"
                  >
                    Password
                  </label>

                  <button
                    type="button"
                    onClick={() =>
                      setError(
                        "Password recovery is not available yet."
                      )
                    }
                    className="text-xs font-medium text-cyan-400 transition hover:text-cyan-300"
                  >
                    Forgot password?
                  </button>

                </div>

                <div className="relative">

                  <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />

                  <input
                    id="password"
                    name="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    autoComplete="current-password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                    disabled={loading}
                    className="h-12 w-full rounded-xl border border-slate-700 bg-slate-800/80 pl-12 pr-12 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        (value) => !value
                      )
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-500 transition hover:bg-slate-700/50 hover:text-slate-300"
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>

                </div>

              </div>

              {/* Remember */}
              <label className="flex cursor-pointer items-center gap-3 text-sm text-slate-400">

                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) =>
                    setRememberMe(
                      event.target.checked
                    )
                  }
                  disabled={loading}
                  className="h-4 w-4 rounded border-slate-600 bg-slate-800 text-cyan-500 focus:ring-cyan-500/30"
                />

                Remember me

              </label>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="group flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:from-cyan-400 hover:to-sky-400 hover:shadow-cyan-500/30 disabled:cursor-not-allowed disabled:opacity-60"
              >

                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign in
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}

              </button>

            </form>

            {/* Registration */}
            <div className="my-7 flex items-center gap-4">

              <div className="h-px flex-1 bg-slate-800" />

              <span className="text-xs uppercase tracking-wider text-slate-600">
                New user
              </span>

              <div className="h-px flex-1 bg-slate-800" />

            </div>

            <div className="text-center">

              <p className="text-sm text-slate-400">
                Don't have an account?
              </p>

              <Link
                to="/register"
                className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-cyan-400 transition hover:text-cyan-300"
              >
                Create an account
                <ArrowRight className="h-4 w-4" />
              </Link>

            </div>

          </div>

          {/* Footer */}
          <div className="mt-6 text-center">

            <p className="text-xs text-slate-600">
              SentinelAI Security Platform
            </p>

            <p className="mt-1 text-xs text-slate-700">
              Authorized access only
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}
