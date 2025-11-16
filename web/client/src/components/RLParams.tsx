import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { motion } from 'motion/react';
import { Brain } from 'lucide-react';

interface RLParamsProps {
  learningRate: string;
  onLearningRateChange: (value: string) => void;
}

export function RLParams({
  learningRate,
  onLearningRateChange,
}: RLParamsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="space-y-1">
        <h4>RL Parameters</h4>
        <p className="text-sm text-muted-foreground">
          Configure reinforcement learning hyperparameters
        </p>
      </div>

      <Card className="p-4 border-border/50">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
              <Brain className="h-4 w-4 text-primary" />
            </div>
            <Label htmlFor="learning-rate">
              Learning Rate
            </Label>
          </div>
          
          <div className="space-y-2">
            <Input
              id="learning-rate"
              type="number"
              step="0.00001"
              min="0.00005"
              max="0.001"
              value={learningRate}
              onChange={(e) => onLearningRateChange(e.target.value)}
              placeholder="0.0001"
              className="border-border/50"
            />
            <p className="text-xs text-muted-foreground">
              Range: 0.00005 - 0.001
            </p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
