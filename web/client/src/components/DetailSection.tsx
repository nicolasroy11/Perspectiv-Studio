import { motion } from 'motion/react';
import { ReactNode } from 'react';

interface DetailSectionProps {
  number: number;
  title: string;
  children: ReactNode;
  delay?: number;
}

export function DetailSection({ number, title, children, delay = 0 }: DetailSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.6, delay, ease: 'easeOut' }}
      className="space-y-4"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-8 h-8 rounded-full border-2 border-primary flex items-center justify-center bg-background">
          <span className="text-primary">{number}</span>
        </div>
        <h3 className="pt-1 text-foreground">{title}</h3>
      </div>
      <div className="pl-12 space-y-3 text-muted-foreground">
        {children}
      </div>
    </motion.div>
  );
}
