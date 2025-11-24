import { motion } from 'motion/react';
import { CheckCircle2, TrendingUp, Target } from 'lucide-react';
import { WaveVisualization } from '../components/WaveVisualization';
import { RSIInfoCard } from '../components/RSIInfoCard';
import { StrategyStep } from '../components/StrategyStep';
import { FlowDiagram } from '../components/FlowDiagram';
import { DetailSection } from '../components/DetailSection';
import { MathFormula } from '../components/MathFormula';

export function RSILowriderPage() {
  return (
    <div className="space-y-12 pb-16">

      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="space-y-8"
      >
        <h1 className="text-foreground">RSI Lowrider</h1>
        <WaveVisualization />
      </motion.div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <RSIInfoCard
          icon={CheckCircle2}
          label="Win Rate:"
          value="85-90%"
          delay={0.1}
        />
        <RSIInfoCard
          icon={TrendingUp}
          label="Market:"
          value="Any, mainly EURUSD"
          delay={0.2}
        />
        <RSIInfoCard
          icon={Target}
          label="Strategy Type:"
          value="Mean Reversion"
          delay={0.3}
        />
      </div>

      {/* Strategy Steps and Flow Diagram */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        {/* Strategy Steps */}
        <div className="space-y-6">
          <StrategyStep
            number={1}
            title="Price drops below RSI=30 → We Buy"
            delay={0.1}
          />
          <StrategyStep
            number={2}
            title="If It Drops a Bit More → We Buy Again"
            delay={0.2}
          />
          <StrategyStep
            number={3}
            title="The Market Usually Bounces → We Take The Small Wins"
            subtitle=""
            delay={0.3}
          />
          <StrategyStep
            number={4}
            title="Price Has Rallied Sufficiently → We Liquidate All At An Average Profit"
            delay={0.4}
          />
        </div>

        {/* Flow Diagram */}
        <FlowDiagram />
      </div>

      {/* Divider */}
      <div className="border-t border-border/30" />

      {/* Detailed Explanations */}
      <div className="space-y-10">

        {/* ===================== */}
        {/* SECTION 1 - EXPOSURE  */}
        {/* ===================== */}

        <DetailSection
          number={1}
          title="Why Multiple Small Entries Are Safer Than One Big Entry"
          delay={0.1}
        >
          <p>
            Lowrider adds entries in fixed-size increments as price moves downward. 
            This keeps exposure growth <strong>linear</strong> rather than exponential.
          </p>

          <div className="bg-card border border-border/30 rounded-lg p-6 shadow-lg shadow-primary/5">
            <MathFormula
              formula="Exposure = \text{lot\_size} \times \text{num\_entries}"
              block
            />
          </div>

          <p className="mt-4">By contrast, martingale grows exposure exponentially:</p>

          <div className="bg-card border border-border/30 rounded-lg p-6 shadow-lg shadow-primary/5">
            <MathFormula
              formula="Exposure_{\text{martingale}} = \sum_{i=0}^{n} \text{lot}_0 \cdot 2^i"
              block
            />
          </div>

          <p className="mt-4 text-primary">
            Lowrider = linear scaling. Martingale = exponential doubling.
          </p>
        </DetailSection>

        {/* ======================= */}
        {/* SECTION 3 - MICRO BOUNCE */}
        {/* ======================= */}

        <DetailSection
          number={3}
          title="Why the 'Micro-Bounce' TP Works"
          delay={0.2}
        >
          <p>
            EURUSD microstructure typically produces 1–4 pip upward corrections even 
            inside strong downtrends. These come from:
          </p>

          <ul className="list-disc list-inside space-y-2 ml-4 mt-3">
            <li>Liquidity refill</li>
            <li>Order-book snapbacks</li>
            <li>High-frequency counter-sweeps</li>
            <li>Profit-taking bursts</li>
            <li>Mean reversion of micro volatility bands</li>
          </ul>

          <p className="mt-4">
            A 3-pip TP exploits these consistently occurring micro-bounces.
          </p>
        </DetailSection>

        {/* ======================= */}
        {/* SECTION 4 - EXPECTED VALUE */}
        {/* ======================= */}

        <DetailSection
          number={4}
          title="The Math Behind the Profit Expectation"
          delay={0.3}
        >
          <p>
            Your live trading stats reflect a strong positive expectation:
          </p>

          <ul className="list-disc list-inside ml-4 mt-3 space-y-1">
            <li>Win probability: <strong>0.88</strong></li>
            <li>Average win: <strong>$11.81</strong></li>
            <li>Loss probability: <strong>0.12</strong></li>
            <li>Average loss: <strong>$5.38</strong></li>
          </ul>

          <div className="bg-card border border-border/30 rounded-lg p-6 shadow-lg shadow-primary/5 mt-4">
            <MathFormula
              formula="E = (0.88)(11.81) - (0.12)(5.38)"
              block
            />
            <MathFormula
              formula="E \approx 10.39 - 0.64 = +9.75"
              block
            />
          </div>

          <p className="mt-4">
            This is a very strong EV for a high-frequency FX strategy.
          </p>
        </DetailSection>

        {/* ======================= */}
        {/* SECTION 6 - HARVESTING */}
        {/* ======================= */}

        <DetailSection
          number={6}
          title="Why Harvesting Improves the EV"
          delay={0.4}
        >
          <p>
            Harvesting means taking a small profit early during weak momentum, then 
            re-entering slightly lower. This improves the weighted entry (AEP) and 
            reduces the required pullback size.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">

            {/* Column A */}
            <div>
              <strong className="block mb-2">A. Average Entry Price (AEP)</strong>
              <div className="bg-card border border-border/30 rounded-lg p-6 shadow-lg shadow-primary/5">
                <MathFormula
                  formula="\text{AEP} = \frac{\sum (\text{entry\_price}_i \cdot \text{lot}_i)}{\sum \text{lot}_i}"
                  block
                />
              </div>
              <p className="mt-3 text-muted-foreground">
                Lower AEP = easier exit.
              </p>
            </div>

            {/* Column B */}
            <div>
              <strong className="block mb-2">B. Reduced TP Distance</strong>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><MathFormula formula="TP_{\text{full}} = AEP + 3\text{ pips}" /></li>
                <li><MathFormula formula="TP_{\text{harvest}} = AEP + 1\text{–}2\text{ pips}" /></li>
              </ul>

              <div className="bg-card border border-border/30 rounded-lg p-6 mt-3 shadow-lg shadow-primary/5">
                <MathFormula
                  formula="\Rightarrow \text{Higher closure probability}"
                  block
                />
              </div>
            </div>

          </div>
        </DetailSection>

        {/* ======================= */}
        {/* SECTION 7 - NOT MARTINGALE */}
        {/* ======================= */}

        <DetailSection
          number={7}
          title="Why It's NOT Martingale (Formal Definition)"
          delay={0.5}
        >
          <p>
            A martingale system requires exponential size increases after losses. 
            Lowrider violates all martingale conditions:
          </p>

          <ul className="list-disc list-inside space-y-2 ml-4 mt-3">
            <li>We never increase lot size after losses</li>
            <li>Entries are triggered only by RSI + spacing signals</li>
            <li>Losses are taken deliberately (no breakeven waiting)</li>
            <li>Exposure grows linearly, not exponentially</li>
          </ul>

          <div className="bg-card border border-border/30 rounded-lg p-4 mt-4 shadow-lg shadow-primary/5">
            <MathFormula
              formula="Exposure(n) = O(n) \quad\text{vs}\quad O(2^n)"
              block
            />
          </div>

          <p className="text-primary mt-4">
            This is structured mean-reversion scalping — not a loss-recovery algorithm.
          </p>
        </DetailSection>

      </div>
    </div>
  );
}
