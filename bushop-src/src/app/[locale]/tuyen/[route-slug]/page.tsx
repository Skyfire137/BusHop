export default function RouteDetailPage({
  params
}: {
  params: { locale: string; 'route-slug': string };
}) {
  return <div>Route detail: {params['route-slug']}</div>;
}
