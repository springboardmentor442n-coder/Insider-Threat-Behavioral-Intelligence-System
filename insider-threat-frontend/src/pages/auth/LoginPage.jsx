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
    <div className="relative min-h-screen w-full overflow-hidden bg-[#020617] text-slate-100 flex items-center justify-center p-4 lg:p-8">
      {/* Background Cyber Glows */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/4 top-1/3 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-[140px]" />
        <div className="absolute right-1/4 bottom-1/4 h-[500px] w-[500px] rounded-full bg-blue-600/10 blur-[120px]" />
        <div className="absolute left-1/2 bottom-10 h-72 w-72 -translate-x-1/2 rounded-full bg-purple-600/10 blur-[100px]" />
      </div>

      {/* Grid Pattern */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(148,163,184,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.5) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative z-10 grid w-full max-w-5xl items-center gap-8 lg:grid-cols-12">
        {/* Left Column: Branding & Features */}
        <div className="hidden space-y-6 lg:col-span-6 lg:block lg:pr-8">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 via-sky-500 to-blue-600 shadow-lg shadow-cyan-500/25">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">SentinelAI</h1>
              <p className="text-xs font-semibold uppercase tracking-wider text-cyan-400">Cyber Intelligence Command</p>
            </div>
          </div>

          <div className="space-y-3">
            <h2 className="text-3xl font-extrabold tracking-tight text-white">
              Insider Threat Behavioral Intelligence Platform
            </h2>
            <p className="text-sm leading-relaxed text-slate-400">
              Enterprise security analytics powered by an unsupervised 7-model machine learning ensemble and CERT Layer 2 behavioral pattern validation.
            </p>
          </div>

          <div className="space-y-3.5 pt-2">
            <div className="flex items-center gap-3 rounded-xl border border-cyan-500/20 bg-slate-900/60 p-3.5 backdrop-blur-md">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
                <Shield className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-200">7-Model Unsupervised Ensemble</h4>
                <p className="text-[11px] text-slate-400">Isolation Forest, OC-SVM, LOF, Elliptic Envelope, PCA, DBSCAN, K-Means</p>
              </div>
            </div>

            <div className="flex items-center gap-3 rounded-xl border border-blue-500/20 bg-slate-900/60 p-3.5 backdrop-blur-md">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400">
                <LockKeyhole className="h-5 w-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-200">CERT Behavioral Validation</h4>
                <p className="text-[11px] text-slate-400">6 behavioral vector baseline evaluation against 1,000 employee population</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Glass Login Form Card */}
        <div className="w-full lg:col-span-6">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-2xl">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white">Sign In</h2>
              <p className="mt-1 text-xs text-slate-400">
                Enter your credentials to access the security command center.
              </p>
            </div>

            {error && (
              <div className="mb-5 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3.5 text-xs text-red-300">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
                <span>{error}</span>
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
        </div>
      </div>
    </div>
  );
}
