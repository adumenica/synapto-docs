'use client';

import React from 'react';
import Link from 'next/link';
import { Settings, Code, Zap, ArrowRight } from 'lucide-react';

const cards = [
  {
    title: 'For Operators',
    description: 'Deploy Synapto, configure integrations, and manage incidents from the UI.',
    link: '/for-operators/getting-started',
    icon: Settings,
    color: 'text-blue-500',
    bg: 'bg-blue-500/10',
  },
  {
    title: 'For Developers',
    description: 'Understand the internals, extend core services, and use the Python SDK.',
    link: '/for-developers/architecture-overview',
    icon: Code,
    color: 'text-[var(--accent)]',
    bg: 'bg-[var(--accent)]/10',
  },
  {
    title: 'Quick Start',
    description: 'The fastest way to get Synapto running in your environment (5 mins).',
    link: '/for-operators/getting-started',
    icon: Zap,
    color: 'text-amber-500',
    bg: 'bg-amber-500/10',
  },
];

export default function LandingCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-16 my-16">
      {cards.map((card, index) => (
        <Link 
          key={card.title} 
          href={card.link}
          className="group relative flex flex-col items-start transition-all duration-300"
        >
          {/* Index Number */}
          <span className="text-[10px] font-mono font-bold text-slate-500 mb-6 tracking-[0.2em] group-hover:text-[var(--accent)] transition-colors">
            0{index + 1}
          </span>

          <div className="mb-6 group-hover:scale-110 group-hover:-translate-y-1 transition-all duration-300">
            <card.icon className={`${card.color} opacity-80 group-hover:opacity-100`} size={28} />
          </div>
          
          <h3 className="relative text-xl font-bold text-white mb-4 tracking-tight inline-block">
            {card.title}
            <span className="absolute -bottom-1 left-0 w-0 h-[1px] bg-[var(--accent)] transition-all duration-300 group-hover:w-full" />
          </h3>
          
          <p className="text-slate-400 text-sm leading-relaxed mb-8 group-hover:text-slate-300 transition-colors">
            {card.description}
          </p>
          
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-slate-500 group-hover:text-[var(--accent)] transition-all">
            Explore <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform" />
          </div>
        </Link>
      ))}
    </div>
  );
}
