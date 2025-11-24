import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';

export function WaveVisualization() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
    };

    resize();
    window.addEventListener('resize', resize);

    let animationFrame: number;
    let phase = 0;

    const draw = () => {
      const rect = canvas.getBoundingClientRect();
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      // Draw threshold line (dashed)
      const threshold = height * 0.5;
      ctx.strokeStyle = '#5bc0ff';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      ctx.moveTo(0, threshold);
      ctx.lineTo(width, threshold);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw smooth wave
      ctx.strokeStyle = '#5bc0ff';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.beginPath();
      for (let x = 0; x <= width; x++) {
        const normalizedX = x / width;
        
        // Create a smooth wave using multiple sine waves
        const wave1 = Math.sin((normalizedX * Math.PI * 2) + phase) * 80;
        const wave2 = Math.sin((normalizedX * Math.PI * 4) + phase * 0.5) * 30;
        const wave3 = Math.sin((normalizedX * Math.PI * 6) + phase * 0.3) * 15;
        
        const y = threshold + wave1 + wave2 + wave3;

        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();

      phase += 0.005;
      animationFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="relative w-full h-48 md:h-64 rounded-xl overflow-hidden"
    >
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ display: 'block' }}
      />
    </motion.div>
  );
}
