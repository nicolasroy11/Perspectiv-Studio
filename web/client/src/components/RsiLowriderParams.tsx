import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { motion } from "motion/react";

interface RSILowriderParamsProps {
  rsiPeriod: string;
  oversoldLevel: string;
  rungSize: string;
  tpSize: string;

  onRsiPeriodChange: (value: string) => void;
  onOversoldLevelChange: (value: string) => void;
  onRungSizeChange: (value: string) => void;
  onTpSizeChange: (value: string) => void;
}

export function RSILowriderParams({
  rsiPeriod,
  oversoldLevel,
  rungSize,
  tpSize,
  onRsiPeriodChange,
  onOversoldLevelChange,
  onRungSizeChange,
  onTpSizeChange,
}: RSILowriderParamsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="space-y-1">
        <h4>RSI Lowrider Parameters</h4>
        <p className="text-sm text-muted-foreground">
          Configure the rules for the Lowrider scalping system
        </p>
      </div>

      {/* RSI Period */}
      <Card className="p-4 border-border/50">
        <div className="space-y-2">
          <Label htmlFor="rsi-period" className="text-sm text-muted-foreground">
            RSI Period
          </Label>
          <Input
            id="rsi-period"
            type="number"
            min="2"
            max="30"
            value={rsiPeriod}
            onChange={(e) => onRsiPeriodChange(e.target.value)}
            placeholder="7"
            className="max-w-[120px] border-border/50"
          />
        </div>
      </Card>

      {/* Oversold Level */}
      <Card className="p-4 border-border/50">
        <div className="space-y-2">
          <Label htmlFor="oversold-level" className="text-sm text-muted-foreground">
            RSI Oversold Level
          </Label>
          <Input
            id="oversold-level"
            type="number"
            min="5"
            max="50"
            value={oversoldLevel}
            onChange={(e) => onOversoldLevelChange(e.target.value)}
            placeholder="30"
            className="max-w-[120px] border-border/50"
          />
        </div>
      </Card>

      {/* Rung Size in Pips */}
      <Card className="p-4 border-border/50">
        <div className="space-y-2">
          <Label htmlFor="rung-size" className="text-sm text-muted-foreground">
            Ladder Spacing (pips)
          </Label>
          <Input
            id="rung-size"
            type="number"
            min="0.1"
            max="20"
            step="0.1"
            value={rungSize}
            onChange={(e) => onRungSizeChange(e.target.value)}
            placeholder="2.0"
            className="max-w-[120px] border-border/50"
          />
        </div>
      </Card>

      {/* TP Size in Pips */}
      <Card className="p-4 border-border/50">
        <div className="space-y-2">
          <Label htmlFor="tp-size" className="text-sm text-muted-foreground">
            TP Target (pips)
          </Label>
          <Input
            id="tp-size"
            type="number"
            min="0.1"
            max="20"
            step="0.1"
            value={tpSize}
            onChange={(e) => onTpSizeChange(e.target.value)}
            placeholder="2.0"
            className="max-w-[120px] border-border/50"
          />
        </div>
      </Card>
    </motion.div>
  );
}
