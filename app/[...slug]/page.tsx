import { notFound } from 'next/navigation';
import { getAllDocSlugs, getDocBySlug } from '@/lib/docs';
import Sidebar from '@/components/Sidebar';
import Markdown from '@/components/Markdown';

interface PageProps {
  params: Promise<{ slug: string[] }>;
}

export const dynamicParams = false;

export async function generateStaticParams() {
  const slugs = getAllDocSlugs();
  // Filter out 'index' as it's handled by app/page.tsx
  return slugs
    .filter(s => s !== 'index')
    .map((slug) => ({
      slug: slug.split('/'),
    }));
}

export default async function DocPage({ params }: PageProps) {
  const { slug } = await params;
  const slugPath = slug.join('/');
  const doc = await getDocBySlug(slugPath);

  if (!doc) {
    notFound();
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 min-w-0 bg-[#0a0a0b]">
        <div className="max-w-4xl mx-auto px-6 py-16 lg:px-12">
          {/* Breadcrumbs or Meta could go here */}
          <div className="mb-12">
            <span className="text-[10px] font-bold text-[var(--accent)] uppercase tracking-widest block mb-2">
              Documentation
            </span>
            <h1 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              {doc.metadata.title}
            </h1>
          </div>
          
          <Markdown content={doc.content} />
          
          <footer className="mt-24 pt-8 border-t border-white/5 text-slate-500 text-sm flex justify-between items-center">
            <span>© 2026 Synapto Operations</span>
            <div className="flex gap-6">
              <a href="https://synaptoops.com" className="hover:text-white transition-colors">Website</a>
              <a href="https://github.com/adumenica/synapto-docs" className="hover:text-white transition-colors">Edit this page</a>
            </div>
          </footer>
        </div>
      </main>
      
      {/* Right Sidebar / TOC could be added here */}
      <aside className="w-64 hidden xl:block shrink-0 sticky top-0 h-screen p-12 overflow-y-auto sidebar-scroll">
         <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">On this page</h4>
         {/* TOC logic could go here */}
      </aside>
    </div>
  );
}
