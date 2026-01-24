<script lang="ts">
  import type { SentimentLabel } from '$lib/types';

  interface Props {
    score: number;
    label: SentimentLabel;
    size?: 'sm' | 'md' | 'lg';
  }

  let { score, label, size = 'md' }: Props = $props();

  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-40 h-40',
    lg: 'w-56 h-56'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-3xl',
    lg: 'text-5xl'
  };

  const labelSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-lg'
  };

  const colorClasses = {
    positive: {
      stroke: 'stroke-emerald-500',
      text: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
      glow: 'drop-shadow-[0_0_20px_rgba(16,185,129,0.5)]'
    },
    neutral: {
      stroke: 'stroke-amber-500',
      text: 'text-amber-500',
      bg: 'bg-amber-500/10',
      glow: 'drop-shadow-[0_0_20px_rgba(245,158,11,0.5)]'
    },
    negative: {
      stroke: 'stroke-rose-500',
      text: 'text-rose-500',
      bg: 'bg-rose-500/10',
      glow: 'drop-shadow-[0_0_20px_rgba(244,63,94,0.5)]'
    }
  };

  const colors = $derived(colorClasses[label] || colorClasses.neutral);
  
  // SVG circle parameters
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const offset = $derived(circumference - (score / 100) * circumference);
</script>

<div class="relative flex items-center justify-center {sizeClasses[size]} {colors.glow}">
  <!-- Background circle -->
  <svg class="absolute inset-0 w-full h-full -rotate-90">
    <circle
      cx="50%"
      cy="50%"
      r="{radius}%"
      fill="none"
      stroke="currentColor"
      stroke-width="8"
      class="text-slate-800"
    />
    <!-- Progress circle -->
    <circle
      cx="50%"
      cy="50%"
      r="{radius}%"
      fill="none"
      stroke-width="8"
      stroke-linecap="round"
      class="{colors.stroke} transition-all duration-1000 ease-out"
      style="stroke-dasharray: {circumference}%; stroke-dashoffset: {offset}%;"
    />
  </svg>
  
  <!-- Center content -->
  <div class="flex flex-col items-center justify-center z-10">
    <span class="font-bold {textSizeClasses[size]} {colors.text}">
      {score.toFixed(0)}%
    </span>
    <span class="uppercase tracking-wider font-medium {labelSizeClasses[size]} {colors.text}">
      {label}
    </span>
  </div>
</div>
