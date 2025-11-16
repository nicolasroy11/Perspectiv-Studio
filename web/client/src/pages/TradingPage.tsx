import { useState, useEffect } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { ChevronDown, ChevronRight, Lightbulb, BarChart3, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useIsMobile } from '../components/ui/use-mobile';
import { Button } from '../components/ui/button';

export function TradingPage() {
  const location = useLocation();
  const isMobile = useIsMobile();
  const [theoriesExpanded, setTheoriesExpanded] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [location.pathname, isMobile]);

  // Initialize sidebar state based on screen size
  useEffect(() => {
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  const isActive = (path: string) => location.pathname === path;
  const isTheoryActive = location.pathname.startsWith('/trading/theories/');

  return (
    <div className="relative">
      {/* Toggle Button - Mobile Only */}
      {isMobile && (
        <Button
          variant="outline"
          size="icon"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="fixed top-20 left-4 z-50 shadow-lg"
        >
          {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      )}

      <div className="flex gap-6">
        {/* Side Navigation - Desktop: Always visible, Mobile: Toggleable */}
        {isMobile ? (
          <AnimatePresence>
            {sidebarOpen && (
              <>
                <motion.aside
                  initial={{ x: -280, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: -280, opacity: 0 }}
                  transition={{ duration: 0.2, ease: 'easeInOut' }}
                  className="fixed left-0 top-16 bottom-0 w-64 bg-background z-40 border-r border-border shadow-lg overflow-y-auto"
                >
                  <nav className="space-y-2 p-4">
                    {/* Theories Section */}
                    <div className="space-y-1">
                      <button
                        onClick={() => setTheoriesExpanded(!theoriesExpanded)}
                        className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                          isTheoryActive
                            ? 'text-foreground bg-muted'
                            : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <Lightbulb className="h-4 w-4" />
                          <span>Theories</span>
                        </div>
                        {theoriesExpanded ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </button>
                      
                      <AnimatePresence>
                        {theoriesExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            className="overflow-hidden"
                          >
                            <div className="ml-6 space-y-1 pt-1">
                              <Link
                                to="/trading/theories/bell-curve-martingale"
                                className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                                  isActive('/trading/theories/bell-curve-martingale')
                                    ? 'text-foreground bg-primary/10'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                                }`}
                              >
                                Bell Curve Martingale
                              </Link>
                              <Link
                                to="/trading/theories/rsi-lowrider"
                                className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                                  isActive('/trading/theories/rsi-lowrider')
                                    ? 'text-foreground bg-primary/10'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                                }`}
                              >
                                RSI Lowrider
                              </Link>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* Backtesting */}
                    <Link
                      to="/trading/backtesting"
                      className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
                        isActive('/trading/backtesting')
                          ? 'text-foreground bg-primary/10'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                      }`}
                    >
                      <BarChart3 className="h-4 w-4" />
                      <span>Backtesting</span>
                    </Link>
                  </nav>
                </motion.aside>

                {/* Backdrop for mobile */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setSidebarOpen(false)}
                  className="fixed inset-0 bg-background/80 backdrop-blur-sm z-30"
                />
              </>
            )}
          </AnimatePresence>
        ) : (
          // Desktop sidebar - always visible
          <aside className="w-64 flex-shrink-0">
            <nav className="sticky top-8 space-y-2">
              {/* Theories Section */}
              <div className="space-y-1">
                <button
                  onClick={() => setTheoriesExpanded(!theoriesExpanded)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-md transition-colors ${
                    isTheoryActive
                      ? 'text-foreground bg-muted'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Lightbulb className="h-4 w-4" />
                    <span>Theories</span>
                  </div>
                  {theoriesExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </button>
                
                <AnimatePresence>
                  {theoriesExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="ml-6 space-y-1 pt-1">
                        <Link
                          to="/trading/theories/bell-curve-martingale"
                          className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                            isActive('/trading/theories/bell-curve-martingale')
                              ? 'text-foreground bg-primary/10'
                              : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                          }`}
                        >
                          Bell Curve Martingale
                        </Link>
                        <Link
                          to="/trading/theories/rsi-lowrider"
                          className={`block px-3 py-2 rounded-md text-sm transition-colors ${
                            isActive('/trading/theories/rsi-lowrider')
                              ? 'text-foreground bg-primary/10'
                              : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                          }`}
                        >
                          RSI Lowrider
                        </Link>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Backtesting */}
              <Link
                to="/trading/backtesting"
                className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
                  isActive('/trading/backtesting')
                    ? 'text-foreground bg-primary/10'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Backtesting</span>
              </Link>
            </nav>
          </aside>
        )}

        {/* Main Content Area */}
        <div className="flex-1 min-w-0">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
