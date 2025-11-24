import { motion } from 'motion/react';
import { LucideIcon } from 'lucide-react';

interface RSIInfoCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  subtitle?: string;
  delay?: number;
}

export function RSIInfoCard({ icon: Icon, label, value, subtitle, delay = 0 }: RSIInfoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      className="relative bg-card border border-border/30 rounded-xl p-6 hover:border-primary/30 transition-colors group"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative">
        <div className="flex items-center gap-2 mb-3">
          <Icon className="w-5 h-5 text-primary" />
          <span className="text-muted-foreground">{label}</span>
        </div>
        <div className="space-y-1">
          <div className="text-foreground">{value}</div>
          {subtitle && <div className="text-muted-foreground">{subtitle}</div>}
        </div>
      </div>
    </motion.div>
  );
}
