export function buildAffiliateUrl(operatorCode: string, bookingUrl: string): string {
  const url = new URL(bookingUrl);
  url.searchParams.set('ref', operatorCode);
  url.searchParams.set('utm_source', 'bushop');
  return url.toString();
}
