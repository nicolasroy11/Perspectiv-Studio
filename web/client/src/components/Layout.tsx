import { Link, useLocation } from 'react-router-dom';
import logo from 'figma:asset/6bba4e57bd584ea86d503171aa48d6e663e7dd59.png';

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Home' },
    { path: '/trading', label: 'Trading' },
    { path: '/music', label: 'Music' },
    { path: '/about', label: 'About' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 backdrop-blur-sm bg-card/30">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center gap-8">
            <Link to="/" className="flex items-center transition-opacity hover:opacity-80">
              <img src={logo} alt="Logo" className="h-8 w-auto" />
            </Link>
            <div className="flex items-center gap-1">
              {menuItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-md transition-all duration-200 ${
                    location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                      ? 'text-foreground bg-primary/10'
                      : 'text-foreground/60 hover:text-foreground hover:bg-muted/50'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
