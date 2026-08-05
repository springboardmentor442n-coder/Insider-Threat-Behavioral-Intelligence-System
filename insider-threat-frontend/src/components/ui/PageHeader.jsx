export default function PageHeader({
  title,
  subtitle,
}) {
  return (
    <div className="mb-8">
      <h1 className="text-5xl font-bold tracking-tight">
        {title}
      </h1>

      <p className="mt-3 text-slate-400 text-lg">
        {subtitle}
      </p>
    </div>
  );
}
