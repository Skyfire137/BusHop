import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { Header } from '@/components/layout/Header';
import { PageLayout } from '@/components/layout/PageLayout';

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const { locale } = params;
  const messages = await getMessages({ locale });
  return (
    <NextIntlClientProvider messages={messages}>
      <Header />
      <PageLayout>
        {children}
      </PageLayout>
    </NextIntlClientProvider>
  );
}
