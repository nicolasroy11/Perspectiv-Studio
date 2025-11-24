import { useEffect, useRef } from 'react';
import katex from 'katex';

interface MathFormulaProps {
  formula: string;
  block?: boolean;
  className?: string;
}

export function MathFormula({ formula, block = false, className = '' }: MathFormulaProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      try {
        katex.render(formula, containerRef.current, {
          displayMode: block,
          throwOnError: false,
          strict: false,
          trust: false,
        });
      } catch (error) {
        console.error('KaTeX rendering error:', error);
        containerRef.current.textContent = formula;
      }
    }
  }, [formula, block]);

  return (
    <div
      ref={containerRef}
      className={`${block ? 'my-4' : 'inline-block'} ${className}`}
    />
  );
}
