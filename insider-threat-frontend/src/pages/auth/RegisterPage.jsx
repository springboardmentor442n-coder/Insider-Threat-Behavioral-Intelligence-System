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
  CheckCircle2,
  Loader2,
  UserPlus,
} from "lucide-react";

import api from "../../lib/axios";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    role: "analyst",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));

    if (error) {
      setError("");
    }

    if (success) {
      setSuccess("");
    }
  };

  const validateForm = () => {
    const username = formData.username.trim();

    if (!username) {
      return "Please enter a username.";
    }

    if (username.length < 3) {
      return "Username must contain at least 3 characters.";
    }

    if (!formData.password) {
      return "Please enter a password.";
    }

    if (formData.password.length < 6) {
      return "Password must contain at least 6 characters.";
    }

    if (!formData.confirmPassword) {
      return "Please confirm your password.";
    }

    if (formData.password !== formData.confirmPassword) {
      return "Passwords do not match.";
    }

    if (!formData.role) {
      return "Please select a role.";
    }

    return null;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/auth/register", {
        username: formData.username.trim(),
        password: formData.password,
        role: formData.role,
      });

      const message =
        response?.data?.message ||
        "Account created successfully.";

      setSuccess(message);

      setFormData({
        username: "",
        password: "",
        confirmPassword: "",
        role: "analyst",
      });

      /*
       * Registration does not automatically log the user in.
       * The user is redirected to the existing login page.
       */
      setTimeout(() => {
        navigate("/login", {
          replace: true,
          state: {
            registered: true,
            username: formData.username.trim(),
          },
        });
      }, 1200);
    } catch (err) {
      let message =
        "Unable to create the account. Please try again.";

      const detail = err?.response?.data?.detail;

      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail
          .map((item) => item?.msg)
          .filter(Boolean)
          .join(", ");
      } else if (detail && typeof detail === "object") {
        message =
          detail.message ||
          detail.detail ||
          message;
      } else if (err?.message) {
        message = err.message;
      }

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">
      <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 py-10">

        {/* Background Glow */}
        <div className="pointer-events-none absolute inset-0">

          <div className="absolute left-1/2 top-1/2 h-[560px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-500/10 blur-[130px]" />

          <div className="absolute left-[8%] top-[12%] h-52 w-52 rounded-full bg-blue-600/10 blur-[100px]" />

          <div className="absolute bottom-[8%] right-[8%] h-60 w-60 rounded-full bg-cyan-400/10 blur-[110px]" />

        </div>

        {/* Background Grid */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(148,163,184,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,0.5) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />

        {/* Main Content */}
        <div className="relative z-10 w-full max-w-md">

          {/* Branding */}
          <div className="mb-7 text-center">

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

          {/* Registration Card */}
          <div className="rounded-3xl border border-slate-800/80 bg-slate-900/80 p-7 shadow-2xl shadow-black/30 backdrop-blur-xl sm:p-8">

            {/* Header */}
            <div className="mb-6">

              <div className="mb-3 flex items-center gap-3">

                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10">
                  <UserPlus className="h-5 w-5 text-cyan-400" />
                </div>

                <div>
                  <h2 className="text-2xl font-semibold text-white">
                    Create account
                  </h2>
                </div>

              </div>

              <p className="text-sm text-slate-400">
                Create an account to access the SentinelAI security platform.
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

            {/* Success */}
            {success && (
              <div className="mb-5 flex items-start gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3">

                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />

                <p className="text-sm leading-5 text-emerald-300">
                  {success}
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
                    placeholder="Choose a username"
                    disabled={loading}
                    className="h-12 w-full rounded-xl border border-slate-700 bg-slate-800/80 pl-12 pr-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                  />

                </div>

              </div>

              {/* Role */}
              <div>

                <label
                  htmlFor="role"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Account Role
                </label>

                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  disabled={loading}
                  className="h-12 w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 text-sm text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <option value="analyst">
                    Analyst
                  </option>

                  <option value="viewer">
                    Viewer
                  </option>

                </select>

                <p className="mt-2 text-xs text-slate-500">
                  Choose the role that matches your access level.
                </p>

              </div>

              {/* Password */}
              <div>

                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Password
                </label>

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
                    autoComplete="new-password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Create a password"
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

              {/* Confirm Password */}
              <div>

                <label
                  htmlFor="confirmPassword"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Confirm Password
                </label>

                <div className="relative">

                  <LockKeyhole className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500" />

                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    autoComplete="new-password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Confirm your password"
                    disabled={loading}
                    className="h-12 w-full rounded-xl border border-slate-700 bg-slate-800/80 pl-12 pr-12 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/10 disabled:cursor-not-allowed disabled:opacity-60"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowConfirmPassword(
                        (value) => !value
                      )
                    }
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-lg p-2 text-slate-500 transition hover:bg-slate-700/50 hover:text-slate-300"
                    aria-label={
                      showConfirmPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>

                </div>

              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="group flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:from-cyan-400 hover:to-sky-400 hover:shadow-cyan-500/30 disabled:cursor-not-allowed disabled:opacity-60"
              >

                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    Create account

                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}

              </button>

            </form>

            {/* Divider */}
            <div className="my-7 flex items-center gap-4">

              <div className="h-px flex-1 bg-slate-800" />

              <span className="text-xs uppercase tracking-wider text-slate-600">
                Existing user
              </span>

              <div className="h-px flex-1 bg-slate-800" />

            </div>

            {/* Login Link */}
            <div className="text-center">

              <p className="text-sm text-slate-400">
                Already have an account?
              </p>

              <Link
                to="/login"
                className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-cyan-400 transition hover:text-cyan-300"
              >
                Sign in

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
