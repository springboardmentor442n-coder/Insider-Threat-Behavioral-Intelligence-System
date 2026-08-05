import { useEffect, useState } from "react";

export default function AnimatedCounter({
  value,
  duration = 1000,
}) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const target = Number(value);

    if (isNaN(target)) {
      setCount(value);
      return;
    }

    let current = 0;

    const increment = target / (duration / 16);

    const timer = setInterval(() => {
      current += increment;

      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value, duration]);

  if (typeof value !== "number") {
    return <>{value}</>;
  }

  return <>{count.toLocaleString()}</>;
}
