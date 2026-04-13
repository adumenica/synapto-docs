import { notFound } from 'next/navigation';
import { getAllDocSlugs, getDocBySlug, getSidebar } from '@/lib/docs';
import DocumentationLayout from '@/components/DocumentationLayout';
import Markdown from '@/components/Markdown';

interface PageProps {
  params: Promise<{ slug: string[] }>;
}



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
  const categories = getSidebar();

  if (!doc) {
    notFound();
  }

  return (
    <DocumentationLayout categories={categories}>
      <div className="flex gap-12">
        <main className="flex-1 min-w-0">
          <div className="pt-4">
            <Markdown content={doc.content} />
          </div>
          
          <footer className="mt-24 pt-8 border-t border-white/5 text-slate-500 text-sm flex justify-between items-center">
            <span>© 2026 Synapto Operations</span>
            <div className="flex gap-6">
              <a href="https://synaptoops.com" className="hover:text-white transition-colors">Website</a>
              <a href="https://github.com/adumenica/synapto-docs" className="hover:text-white transition-colors">Edit this page</a>
            </div>
          </footer>
        </main>
        
        {/* Right Sidebar / TOC - Hidden on mobile/tablet */}
        <aside className="w-64 hidden xl:block shrink-0 sticky top-0 h-screen py-16 overflow-y-auto sidebar-scroll">
           <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">On this page</h4>
           {/* TOC logic could go here */}
        </aside>
      </div>
    </DocumentationLayout>
  );
}
