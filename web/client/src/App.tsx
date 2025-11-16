import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { TradingPage } from './pages/TradingPage';
import { BacktestingPage } from './pages/BacktestingPage';
import { BellCurveMartingalePage } from './pages/BellCurveMartingalePage';
import { RSILowriderPage } from './pages/RSILowriderPage';
import { MusicPage } from './pages/MusicPage';
import { AboutPage } from './pages/AboutPage';

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/trading-automation" element={<Navigate to="/trading/backtesting" replace />} />
          <Route path="/trading" element={<TradingPage />}>
            <Route index element={<Navigate to="/trading/backtesting" replace />} />
            <Route path="backtesting" element={<BacktestingPage />} />
            <Route path="theories/bell-curve-martingale" element={<BellCurveMartingalePage />} />
            <Route path="theories/rsi-lowrider" element={<RSILowriderPage />} />
          </Route>
          <Route path="/music" element={<MusicPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}
