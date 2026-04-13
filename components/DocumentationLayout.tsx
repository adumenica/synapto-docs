'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import MobileHeader from './MobileHeader';
import { usePathname } from 'next/navigation';
import { SidebarCategory } from '@/lib/docs';

interface DocumentationLayoutProps {
  children: React.ReactNode;
  categories: SidebarCategory[];
}

export default function DocumentationLayout({ children, categories }: DocumentationLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const pathname = usePathname();

  // Close sidebar when navigating on mobile
  useEffect(() => {
    setIsSidebarOpen(false);
  }, [pathname]);

  return (
    <div className="flex min-h-screen bg-[#0a0a0b]">
      {/* Mobile Backdrop */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Main Sidebar (Desktop fixed, Mobile Slide-over) */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-[var(--sidebar-w)] transform transition-transform duration-300 ease-in-out bg-[#0a0a0b]
        md:relative md:translate-x-0
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar categories={categories} />
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <MobileHeader 
          isOpen={isSidebarOpen} 
          onToggle={() => setIsSidebarOpen(!isSidebarOpen)} 
        />
        
        <main className="flex-1 min-w-0">
          <div className="max-w-4xl mx-auto px-6 py-12 lg:px-12 lg:py-16">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
