import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import {
  TrendingUp,
  Brain,
  Coins,
  Calendar,
  Sparkles,
  ArrowRight,
  Clock,
} from "lucide-react";
import { motion } from "motion/react";
import { RulesBasedParams } from "../components/RulesBasedParams";
import { RLParams } from "../components/RLParams";

export function BacktestingPage() {
  const [asset, setAsset] = useState<string>("");
  const [tradingType, setTradingType] = useState<string>("");
  const [frequency, setFrequency] = useState<string>("");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  // Rules-based parameters
  const [rsiEnabled, setRsiEnabled] = useState(false);
  const [rsiValue, setRsiValue] = useState("14");
  const [emaEnabled, setEmaEnabled] = useState(false);
  const [emaShortPeriod, setEmaShortPeriod] = useState("12");
  const [emaLongPeriod, setEmaLongPeriod] = useState("26");

  // RL parameters
  const [learningRate, setLearningRate] = useState("0.0001");

  const handleGo = async () => {
    setIsLoading(true);

    const params: any = {
      asset,
      tradingType,
      frequency,
      dateFrom,
      dateTo,
    };

    if (tradingType === "rules-based") {
      params.rulesBased = {
        rsi: rsiEnabled
          ? { enabled: true, period: parseInt(rsiValue) }
          : { enabled: false },
        emaCrossover: emaEnabled
          ? {
              enabled: true,
              shortPeriod: parseInt(emaShortPeriod),
              longPeriod: parseInt(emaLongPeriod),
            }
          : { enabled: false },
      };
    }

    if (tradingType === "rl") {
      params.rl = {
        learningRate: parseFloat(learningRate),
      };
    }

    try {
      console.log("Sending to backend:", params);

      const res = await fetch(
        "https://trader-api.perspectivstudio.com/api/backtest/run",
        // "http://localhost:8000/api/backtest/run",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(params),
        }
      );

      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }

      const data = await res.json();
      console.log("BACKTEST RESULT:", data);

      // TODO: forward 'data' into a results page or widget
    } catch (err) {
      console.error("Request failed:", err);
      alert("Something went wrong — check console logs");
    }

    setIsLoading(false);
  };

  const isFormValid =
    asset && tradingType && frequency && dateFrom && dateTo;

  const getTradingTypeIcon = () => {
    switch (tradingType) {
      case "rules-based":
        return <TrendingUp className="h-4 w-4" />;
      case "rl":
        return <Brain className="h-4 w-4" />;
      case "llm":
        return <Sparkles className="h-4 w-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-3">
            Backtesting
            <Badge
              variant="outline"
              className="border-primary/50 text-primary"
            >
              Beta
            </Badge>
          </h1>
          <p className="text-muted-foreground">
            Configure your automated trading strategy
          </p>
        </div>
      </div>

      <Card className="border-border/50 shadow-lg shadow-primary/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle>Backtesting Configuration</CardTitle>
              <CardDescription>
                Select your asset, trading type, and date range
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <motion.div
              className="space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <label
                htmlFor="asset"
                className="text-sm text-muted-foreground flex items-center gap-2"
              >
                <Coins className="h-4 w-4" />
                Asset
              </label>
              <Select value={asset} onValueChange={setAsset}>
                <SelectTrigger
                  id="asset"
                  className="border-border/50"
                >
                  <SelectValue placeholder="Select an asset" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BTCUSDT">
                    BTCUSDT
                  </SelectItem>
                  <SelectItem value="EURUSD">EURUSD</SelectItem>
                </SelectContent>
              </Select>
            </motion.div>

            <motion.div
              className="space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <label
                htmlFor="trading-type"
                className="text-sm text-muted-foreground flex items-center gap-2"
              >
                <Brain className="h-4 w-4" />
                Trading Type
              </label>
              <Select
                value={tradingType}
                onValueChange={setTradingType}
              >
                <SelectTrigger
                  id="trading-type"
                  className="border-border/50"
                >
                  <SelectValue placeholder="Select a trading type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="rules-based">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Rules based
                    </div>
                  </SelectItem>
                  <SelectItem value="rl">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      RL
                    </div>
                  </SelectItem>
                  <SelectItem value="llm">
                    <div className="flex items-center gap-2">
                      <Sparkles className="h-4 w-4" />
                      LLM
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </motion.div>

            <motion.div
              className="space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <label
                htmlFor="frequency"
                className="text-sm text-muted-foreground flex items-center gap-2"
              >
                <Clock className="h-4 w-4" />
                Frequency
              </label>
              <Select
                value={frequency}
                onValueChange={setFrequency}
              >
                <SelectTrigger
                  id="frequency"
                  className="border-border/50"
                >
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1m">1 minute</SelectItem>
                  <SelectItem value="5m">5 minutes</SelectItem>
                  <SelectItem value="15m">
                    15 minutes
                  </SelectItem>
                  <SelectItem value="30m">
                    30 minutes
                  </SelectItem>
                  <SelectItem value="1h">1 hour</SelectItem>
                  <SelectItem value="4h">4 hours</SelectItem>
                </SelectContent>
              </Select>
            </motion.div>

            <motion.div
              className="space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <label
                htmlFor="date-from"
                className="text-sm text-muted-foreground flex items-center gap-2"
              >
                <Calendar className="h-4 w-4" />
                Date From
              </label>
              <Input
                id="date-from"
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="border-border/50"
              />
            </motion.div>

            <motion.div
              className="space-y-2"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <label
                htmlFor="date-to"
                className="text-sm text-muted-foreground flex items-center gap-2"
              >
                <Calendar className="h-4 w-4" />
                Date To
              </label>
              <Input
                id="date-to"
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="border-border/50"
              />
            </motion.div>
          </div>

          {/* Trading Type Specific Parameters */}
          {tradingType === "rules-based" && (
            <>
              <Separator className="my-6" />
              <RulesBasedParams
                rsiEnabled={rsiEnabled}
                rsiValue={rsiValue}
                emaEnabled={emaEnabled}
                emaShortPeriod={emaShortPeriod}
                emaLongPeriod={emaLongPeriod}
                onRsiEnabledChange={setRsiEnabled}
                onRsiValueChange={setRsiValue}
                onEmaEnabledChange={setEmaEnabled}
                onEmaShortPeriodChange={setEmaShortPeriod}
                onEmaLongPeriodChange={setEmaLongPeriod}
              />
            </>
          )}

          {tradingType === "rl" && (
            <>
              <Separator className="my-6" />
              <RLParams
                learningRate={learningRate}
                onLearningRateChange={setLearningRate}
              />
            </>
          )}

          <motion.div
            className="flex justify-end pt-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.35 }}
          >
            <Button
              onClick={handleGo}
              disabled={!isFormValid || isLoading}
              className="px-8 bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20 hover:shadow-primary/30 transition-all duration-200 group"
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  Go!
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </Button>
          </motion.div>

          {isFormValid && !isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-lg border border-primary/20 bg-gradient-to-br from-primary/5 to-transparent p-4 backdrop-blur-sm"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                <h3>Selected Configuration</h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Asset
                  </p>
                  <div className="flex items-center gap-2">
                    <Coins className="h-4 w-4 text-primary" />
                    <span className="text-foreground">
                      {asset}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Frequency
                  </p>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-primary" />
                    <span className="text-foreground">
                      {frequency}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Trading Type
                  </p>
                  <div className="flex items-center gap-2">
                    {getTradingTypeIcon()}
                    <span className="text-foreground">
                      {tradingType}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Date From
                  </p>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    <span className="text-foreground">
                      {dateFrom}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Date To
                  </p>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    <span className="text-foreground">
                      {dateTo}
                    </span>
                  </div>
                </div>
              </div>

              {/* Rules-based parameters summary */}
              {tradingType === "rules-based" &&
                (rsiEnabled || emaEnabled) && (
                  <>
                    <Separator className="my-3" />
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground">
                        Active Indicators
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {rsiEnabled && (
                          <Badge
                            variant="secondary"
                            className="bg-primary/10 text-primary border-primary/20"
                          >
                            RSI: {rsiValue}
                          </Badge>
                        )}
                        {emaEnabled && (
                          <Badge
                            variant="secondary"
                            className="bg-primary/10 text-primary border-primary/20"
                          >
                            EMA: {emaShortPeriod}/
                            {emaLongPeriod}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </>
                )}

              {/* RL parameters summary */}
              {tradingType === "rl" && (
                <>
                  <Separator className="my-3" />
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">
                      Hyperparameters
                    </p>
                    <Badge
                      variant="secondary"
                      className="bg-primary/10 text-primary border-primary/20"
                    >
                      Learning Rate: {learningRate}
                    </Badge>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}