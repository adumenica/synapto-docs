'use client';

import React from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

interface MobileHeaderProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function MobileHeader({ isOpen, onToggle }: MobileHeaderProps) {
  return (
    <header className="sticky top-0 z-40 w-full md:hidden border-b border-white/5 bg-[#0a0a0b]/80 backdrop-blur-lg">
      <div className="flex h-16 items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-[var(--accent)] rounded-lg flex items-center justify-center font-bold text-white">
            S
          </div>
          <span className="font-bold text-lg tracking-tight">Synapto Docs</span>
        </Link>
        
        <button
          onClick={onToggle}
          className="p-2 text-slate-400 hover:text-white transition-colors"
          aria-label={isOpen ? "Close menu" : "Open menu"}
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </header>
  );
}
