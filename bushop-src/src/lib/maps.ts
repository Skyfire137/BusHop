export function buildMapsDeeplink(lat: number, lng: number): string {
  return `https://maps.google.com/maps?q=${lat},${lng}`;
}
