import "./globals.css";

export const metadata = {
  title: "AutoAce AI",
  description: "Production Call Audio Analysis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}