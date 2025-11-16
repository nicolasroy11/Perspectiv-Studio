import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { TrendingUp } from 'lucide-react';

export function BellCurveMartingalePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-3">
          Bell Curve Martingale
          <Badge variant="outline" className="border-primary/50 text-primary">
            Theory
          </Badge>
        </h1>
        <p className="text-muted-foreground">
          Statistical distribution-based position sizing strategy
        </p>
      </div>

      <Card className="border-border/50 shadow-lg shadow-primary/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle>Theory Overview</CardTitle>
              <CardDescription>
                Combining bell curve distribution with martingale strategy
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            This theory page is under development. Content coming soon...
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
