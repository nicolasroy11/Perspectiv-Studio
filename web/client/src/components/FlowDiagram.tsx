import { motion } from 'motion/react';
import { ArrowDown } from 'lucide-react';

export function FlowDiagram() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay: 0.4, ease: 'easeOut' }}
      className="bg-card border border-border/30 rounded-xl p-8 hover:border-primary/30 transition-colors"
    >
      <div className="flex flex-col items-center gap-4 max-w-xs mx-auto">
        {/* RSI */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.6 }}
          className="flex items-center gap-3"
        >
          <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
          <span className="text-foreground">RSI Low</span>
        </motion.div>

        {/* Arrow */}
        <motion.div
          initial={{ opacity: 0, scaleY: 0 }}
          animate={{ opacity: 1, scaleY: 1 }}
          transition={{ duration: 0.3, delay: 0.8 }}
        >
          <ArrowDown className="w-5 h-5 text-muted-foreground" />
        </motion.div>

        {/* Bounce */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 1.0 }}
          className="text-primary"
        >
          First Buy
        </motion.div>

        {/* Arrow */}
        <motion.div
          initial={{ opacity: 0, scaleY: 0 }}
          animate={{ opacity: 1, scaleY: 1 }}
          transition={{ duration: 0.3, delay: 1.2 }}
        >
          <ArrowDown className="w-5 h-5 text-muted-foreground" />
        </motion.div>

        {/* Bounce */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 1.4 }}
          className="text-primary"
        >
          Harvest Small Movements
        </motion.div>

        {/* Arrow */}
        <motion.div
          initial={{ opacity: 0, scaleY: 0 }}
          animate={{ opacity: 1, scaleY: 1 }}
          transition={{ duration: 0.3, delay: 1.6 }}
        >
          <ArrowDown className="w-5 h-5 text-muted-foreground" />
        </motion.div>

        {/* Take Profit */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 1.8 }}
          className="text-primary"
        >
          Take Profit
        </motion.div>
      </div>
    </motion.div>
  );
}
