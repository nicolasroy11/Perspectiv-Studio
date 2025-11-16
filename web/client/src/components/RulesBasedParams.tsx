import { Checkbox } from './ui/checkbox';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { motion } from 'motion/react';

interface RulesBasedParamsProps {
  rsiEnabled: boolean;
  rsiValue: string;
  emaEnabled: boolean;
  emaShortPeriod: string;
  emaLongPeriod: string;
  onRsiEnabledChange: (checked: boolean) => void;
  onRsiValueChange: (value: string) => void;
  onEmaEnabledChange: (checked: boolean) => void;
  onEmaShortPeriodChange: (value: string) => void;
  onEmaLongPeriodChange: (value: string) => void;
}

export function RulesBasedParams({
  rsiEnabled,
  rsiValue,
  emaEnabled,
  emaShortPeriod,
  emaLongPeriod,
  onRsiEnabledChange,
  onRsiValueChange,
  onEmaEnabledChange,
  onEmaShortPeriodChange,
  onEmaLongPeriodChange,
}: RulesBasedParamsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="space-y-1">
        <h4>Strategy Parameters</h4>
        <p className="text-sm text-muted-foreground">
          Configure technical indicators for rules-based trading
        </p>
      </div>

      <div className="space-y-4">
        {/* RSI Parameter */}
        <Card className="p-4 border-border/50">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="rsi-enabled"
                checked={rsiEnabled}
                onCheckedChange={onRsiEnabledChange}
              />
              <Label
                htmlFor="rsi-enabled"
                className="cursor-pointer"
              >
                RSI (Relative Strength Index)
              </Label>
            </div>
            
            {rsiEnabled && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="pl-6 space-y-2"
              >
                <Label htmlFor="rsi-value" className="text-sm text-muted-foreground">
                  Period
                </Label>
                <Input
                  id="rsi-value"
                  type="number"
                  min="2"
                  max="30"
                  value={rsiValue}
                  onChange={(e) => onRsiValueChange(e.target.value)}
                  placeholder="14"
                  className="max-w-[120px] border-border/50"
                />
                <p className="text-xs text-muted-foreground">
                  Range: 2-30
                </p>
              </motion.div>
            )}
          </div>
        </Card>

        {/* EMA Crossover Parameter */}
        <Card className="p-4 border-border/50">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="ema-enabled"
                checked={emaEnabled}
                onCheckedChange={onEmaEnabledChange}
              />
              <Label
                htmlFor="ema-enabled"
                className="cursor-pointer"
              >
                EMA Crossover
              </Label>
            </div>
            
            {emaEnabled && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="pl-6 space-y-4"
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ema-short" className="text-sm text-muted-foreground">
                      Short Period
                    </Label>
                    <Input
                      id="ema-short"
                      type="number"
                      min="2"
                      max="500"
                      value={emaShortPeriod}
                      onChange={(e) => onEmaShortPeriodChange(e.target.value)}
                      placeholder="12"
                      className="border-border/50"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="ema-long" className="text-sm text-muted-foreground">
                      Long Period
                    </Label>
                    <Input
                      id="ema-long"
                      type="number"
                      min="2"
                      max="500"
                      value={emaLongPeriod}
                      onChange={(e) => onEmaLongPeriodChange(e.target.value)}
                      placeholder="26"
                      className="border-border/50"
                    />
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  Range: 2-500 for both periods
                </p>
              </motion.div>
            )}
          </div>
        </Card>
      </div>
    </motion.div>
  );
}
