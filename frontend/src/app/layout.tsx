export const metadata = {
  title: 'Virtuoso MES | Управление производством',
  description: 'Современная система управления производством',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
}
