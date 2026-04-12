import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const DOCS_DIR = path.join(process.cwd(), 'content/docs');

export interface DocMetadata {
  title: string;
  slug: string;
  category?: string;
  order?: number;
}

export interface SidebarItem {
  title: string;
  slug: string;
}

export interface SidebarCategory {
  title: string;
  items: SidebarItem[];
}

export function getAllDocSlugs() {
  const files: string[] = [];
  
  function scan(dir: string, base = '') {
    const list = fs.readdirSync(dir);
    for (const item of list) {
      const fullPath = path.join(dir, item);
      const relativePath = path.join(base, item);
      if (fs.statSync(fullPath).isDirectory()) {
        scan(fullPath, relativePath);
      } else if (item.endsWith('.md')) {
        files.push(relativePath.replace(/\\/g, '/').replace(/.md$/, ''));
      }
    }
  }

  if (fs.existsSync(DOCS_DIR)) {
    scan(DOCS_DIR);
  }
  return files;
}

export async function getDocBySlug(slug: string) {
  const realSlug = slug === 'index' ? 'index' : slug.replace(/\/$/, '');
  let fullPath = path.join(DOCS_DIR, `${realSlug}.md`);
  
  if (!fs.existsSync(fullPath)) {
    // Try directory index
    fullPath = path.join(DOCS_DIR, realSlug, 'index.md');
    if (!fs.existsSync(fullPath)) {
        // Try fallback to README if it's the root or a dir
        fullPath = path.join(DOCS_DIR, realSlug, 'README.md');
        if (!fs.existsSync(fullPath)) return null;
    }
  }

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);

  return {
    metadata: {
      title: data.title || (realSlug === 'index' ? 'Introduction' : realSlug.split('/').pop()),
      slug: realSlug,
      ...data,
    } as DocMetadata,
    content,
  };
}

export function getSidebar(): SidebarCategory[] {
  const categories: Record<string, SidebarItem[]> = {};
  const slugs = getAllDocSlugs();

  slugs.forEach(slug => {
    const parts = slug.split('/');
    let categoryName = 'General';
    let title = parts[parts.length - 1];

    if (parts.length > 1) {
      categoryName = parts[0].replace(/-/g, ' ');
      // Capitalize
      categoryName = categoryName.charAt(0).toUpperCase() + categoryName.slice(1);
    }

    if (!categories[categoryName]) categories[categoryName] = [];
    categories[categoryName].push({
      title: title.replace(/-/g, ' ').charAt(0).toUpperCase() + title.replace(/-/g, ' ').slice(1),
      slug: slug === 'index' ? '/' : `/${slug}`,
    });
  });

  return Object.keys(categories).map(cat => ({
    title: cat,
    items: categories[cat],
  }));
}
