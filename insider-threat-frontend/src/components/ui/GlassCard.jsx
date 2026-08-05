export default function GlassCard({
  children,
  className = "",
}) {
  return (
    <div
      className={`
        rounded-2xl
        border border-white/10
        bg-white/5
        backdrop-blur-xl
        shadow-2xl
        transition-all
        duration-300
        hover:border-cyan-400/40
        hover:shadow-cyan-500/20
        ${className}
      `}
    >
      {children}
    </div>
  );
}
