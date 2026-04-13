import { getDocBySlug, getSidebar } from '@/lib/docs';
import DocumentationLayout from '@/components/DocumentationLayout';
import Markdown from '@/components/Markdown';
import LandingCards from '@/components/LandingCards';
import { notFound } from 'next/navigation';

export default async function Home() {
  const doc = await getDocBySlug('index');
  const categories = getSidebar();

  if (!doc) {
    notFound();
  }

  return (
    <DocumentationLayout categories={categories}>
      <div className="max-w-4xl mx-auto">
        <div className="pt-4">
          <Markdown content={doc.content} />
        </div>
        
        <h2 className="text-2xl font-bold text-white mt-16 mb-8 tracking-tight">
          Where to start
        </h2>
        
        <LandingCards />
      </div>
    </DocumentationLayout>
  );
}
