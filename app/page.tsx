import DocPage from './[...slug]/page';

export default function Home() {
  // @ts-ignore - params for root
  return <DocPage params={Promise.resolve({ slug: ['index'] })} />;
}
