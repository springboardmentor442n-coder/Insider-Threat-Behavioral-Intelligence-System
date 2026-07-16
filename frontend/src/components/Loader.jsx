import { motion } from 'framer-motion';
import './Loader.css';

export default function Loader({ full = false, label = 'Loading' }) {
  return (
    <div className={full ? 'loader loader--full' : 'loader'}>
      <div className="loader__scan">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="loader__bar"
            animate={{ scaleY: [0.3, 1, 0.3] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.15,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
      <span className="loader__label eyebrow">{label}</span>
    </div>
  );
}
