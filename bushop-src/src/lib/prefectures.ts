export interface Prefecture {
  id: string
  name_vi: string
  name_ja: string
  name_en: string
}

export const PREFECTURES: Prefecture[] = [
  { id: 'tokyo', name_vi: 'Tokyo', name_ja: '東京', name_en: 'Tokyo' },
  { id: 'osaka', name_vi: 'Osaka', name_ja: '大阪', name_en: 'Osaka' },
  { id: 'kyoto', name_vi: 'Kyoto', name_ja: '京都', name_en: 'Kyoto' },
  { id: 'nagoya', name_vi: 'Nagoya', name_ja: '名古屋', name_en: 'Nagoya' },
  { id: 'sapporo', name_vi: 'Sapporo', name_ja: '札幌', name_en: 'Sapporo' },
  { id: 'fukuoka', name_vi: 'Fukuoka', name_ja: '福岡', name_en: 'Fukuoka' },
  { id: 'hiroshima', name_vi: 'Hiroshima', name_ja: '広島', name_en: 'Hiroshima' },
  { id: 'sendai', name_vi: 'Sendai', name_ja: '仙台', name_en: 'Sendai' },
  { id: 'kanazawa', name_vi: 'Kanazawa', name_ja: '金沢', name_en: 'Kanazawa' },
  { id: 'naha', name_vi: 'Naha (Okinawa)', name_ja: '那覇', name_en: 'Naha' },
  { id: 'yokohama', name_vi: 'Yokohama', name_ja: '横浜', name_en: 'Yokohama' },
  { id: 'kobe', name_vi: 'Kobe', name_ja: '神戸', name_en: 'Kobe' },
  { id: 'nagasaki', name_vi: 'Nagasaki', name_ja: '長崎', name_en: 'Nagasaki' },
  { id: 'kumamoto', name_vi: 'Kumamoto', name_ja: '熊本', name_en: 'Kumamoto' },
  { id: 'matsuyama', name_vi: 'Matsuyama', name_ja: '松山', name_en: 'Matsuyama' },
  { id: 'takamatsu', name_vi: 'Takamatsu', name_ja: '高松', name_en: 'Takamatsu' },
  { id: 'kochi', name_vi: 'Kochi', name_ja: '高知', name_en: 'Kochi' },
  { id: 'tokushima', name_vi: 'Tokushima', name_ja: '徳島', name_en: 'Tokushima' },
  { id: 'tottori', name_vi: 'Tottori', name_ja: '鳥取', name_en: 'Tottori' },
  { id: 'matsue', name_vi: 'Matsue', name_ja: '松江', name_en: 'Matsue' },
  { id: 'okayama', name_vi: 'Okayama', name_ja: '岡山', name_en: 'Okayama' },
  { id: 'yamaguchi', name_vi: 'Yamaguchi', name_ja: '山口', name_en: 'Yamaguchi' },
  { id: 'saga', name_vi: 'Saga', name_ja: '佐賀', name_en: 'Saga' },
  { id: 'oita', name_vi: 'Oita', name_ja: '大分', name_en: 'Oita' },
  { id: 'miyazaki', name_vi: 'Miyazaki', name_ja: '宮崎', name_en: 'Miyazaki' },
  { id: 'kagoshima', name_vi: 'Kagoshima', name_ja: '鹿児島', name_en: 'Kagoshima' },
  { id: 'niigata', name_vi: 'Niigata', name_ja: '新潟', name_en: 'Niigata' },
  { id: 'toyama', name_vi: 'Toyama', name_ja: '富山', name_en: 'Toyama' },
  { id: 'fukui', name_vi: 'Fukui', name_ja: '福井', name_en: 'Fukui' },
  { id: 'shizuoka', name_vi: 'Shizuoka', name_ja: '静岡', name_en: 'Shizuoka' },
  { id: 'hamamatsu', name_vi: 'Hamamatsu', name_ja: '浜松', name_en: 'Hamamatsu' },
  { id: 'gifu', name_vi: 'Gifu', name_ja: '岐阜', name_en: 'Gifu' },
  { id: 'tsu', name_vi: 'Tsu (Mie)', name_ja: '津', name_en: 'Tsu' },
  { id: 'otsu', name_vi: 'Otsu (Shiga)', name_ja: '大津', name_en: 'Otsu' },
  { id: 'nara', name_vi: 'Nara', name_ja: '奈良', name_en: 'Nara' },
  { id: 'wakayama', name_vi: 'Wakayama', name_ja: '和歌山', name_en: 'Wakayama' },
  { id: 'mito', name_vi: 'Mito (Ibaraki)', name_ja: '水戸', name_en: 'Mito' },
  { id: 'utsunomiya', name_vi: 'Utsunomiya', name_ja: '宇都宮', name_en: 'Utsunomiya' },
  { id: 'maebashi', name_vi: 'Maebashi', name_ja: '前橋', name_en: 'Maebashi' },
  { id: 'saitama', name_vi: 'Saitama', name_ja: 'さいたま', name_en: 'Saitama' },
  { id: 'chiba', name_vi: 'Chiba', name_ja: '千葉', name_en: 'Chiba' },
  { id: 'kofu', name_vi: 'Kofu (Yamanashi)', name_ja: '甲府', name_en: 'Kofu' },
  { id: 'nagano', name_vi: 'Nagano', name_ja: '長野', name_en: 'Nagano' },
  { id: 'aomori', name_vi: 'Aomori', name_ja: '青森', name_en: 'Aomori' },
  { id: 'morioka', name_vi: 'Morioka (Iwate)', name_ja: '盛岡', name_en: 'Morioka' },
  { id: 'akita', name_vi: 'Akita', name_ja: '秋田', name_en: 'Akita' },
  { id: 'yamagata', name_vi: 'Yamagata', name_ja: '山形', name_en: 'Yamagata' },
  { id: 'fukushima', name_vi: 'Fukushima', name_ja: '福島', name_en: 'Fukushima' },
]

export function searchPrefectures(query: string): Prefecture[] {
  if (!query || query.length < 1) return []
  const q = query.toLowerCase()
  return PREFECTURES.filter(
    (p) =>
      p.name_vi.toLowerCase().includes(q) ||
      p.name_en.toLowerCase().includes(q) ||
      p.name_ja.includes(q),
  ).slice(0, 6)
}
