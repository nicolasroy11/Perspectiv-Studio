import { motion } from 'motion/react';

interface StrategyStepProps {
  number: number;
  title: string;
  subtitle?: string;
  delay?: number;
}

export function StrategyStep({ number, title, subtitle, delay = 0 }: StrategyStepProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      className="flex gap-4 items-start group"
    >
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center border border-primary/30 group-hover:bg-primary/30 transition-colors">
        <span className="text-primary">{number}</span>
      </div>
      <div className="flex-1 pt-1">
        <div className="text-foreground">{title}</div>
        {subtitle && <div className="text-muted-foreground mt-1">{subtitle}</div>}
      </div>
    </motion.div>
  );
}
