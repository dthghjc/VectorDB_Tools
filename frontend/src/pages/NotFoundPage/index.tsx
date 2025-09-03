import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  const { t } = useTranslation();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center space-y-6 bg-background p-4 text-center">
      <div className="space-y-2">
        <h1 className="text-5xl font-bold tracking-tighter sm:text-7xl">404</h1>
        <p className="text-2xl font-medium text-muted-foreground">
          {t('notFound.title')}
        </p>
      </div>
      <p className="max-w-md text-muted-foreground">
        {t('notFound.description')}
      </p>
      <Button asChild>
        <Link to="/">{t('notFound.backHome')}</Link>
      </Button>
    </div>
  );
}
