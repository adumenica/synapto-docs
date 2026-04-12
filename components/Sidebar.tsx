import Link from 'next/link';
import { getSidebar } from '@/lib/docs';

export default function Sidebar() {
  const categories = getSidebar();

  return (
    <aside className="w-[var(--sidebar-w)] border-r border-white/5 bg-[#0a0a0b] h-screen sticky top-0 overflow-y-auto sidebar-scroll shrink-0 hidden md:block">
      <div className="p-6 border-b border-white/5">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-[var(--accent)] rounded-lg flex items-center justify-center font-bold text-white group-hover:scale-110 transition-transform">
            S
          </div>
          <span className="font-bold text-lg tracking-tight group-hover:text-white transition-colors">Synapto Docs</span>
        </Link>
      </div>

      <nav className="p-6 space-y-8">
        {categories.map((cat) => (
          <div key={cat.title}>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-4">
              {cat.title}
            </h4>
            <ul className="space-y-1">
              {cat.items.map((item) => (
                <li key={item.slug}>
                  <Link
                    href={item.slug}
                    className="block py-1.5 text-sm text-slate-400 hover:text-[var(--accent)] transition-colors"
                  >
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
