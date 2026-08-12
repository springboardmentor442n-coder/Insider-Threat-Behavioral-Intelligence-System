/**
 * PageHeader — Shared command-center page header
 *
 * Used across all authenticated pages to provide a consistent
 * visual introduction: icon + title + subtitle + optional badge.
 *
 * Props:
 *   icon       — Lucide icon component
 *   title      — Page title string
 *   subtitle   — Short descriptive subtitle
 *   badge      — Optional React node rendered on the right
 *   children   — Optional right-side content (buttons, badges, etc.)
 *   className  — Extra wrapper classes
 */
export default function PageHeader({
  icon: Icon,
  title,
  subtitle,
  badge,
  children,
  className = "",
}) {
  return (
    <section
      className={`
        relative overflow-hidden
        rounded-2xl
        border border-cyan-500/20
        bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-slate-950/90
        p-5 md:p-6
        backdrop-blur-xl
        shadow-lg shadow-cyan-950/20
        ${className}
      `}
    >
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: icon + title + subtitle */}
        <div className="flex items-center gap-3 min-w-0">
          {Icon && (
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 via-blue-500/20 to-indigo-500/20 border border-cyan-500/30 text-cyan-400 shadow-md">
              <Icon className="h-6 w-6 text-cyan-400" />
            </div>
          )}

          <div className="min-w-0">
            {title && (
              <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white truncate">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="mt-0.5 text-xs text-slate-400 line-clamp-2">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Right: badge or children */}
        {(badge || children) && (
          <div className="flex items-center gap-2 shrink-0 flex-wrap">
            {badge}
            {children}
          </div>
        )}
      </div>
    </section>
  );
}
