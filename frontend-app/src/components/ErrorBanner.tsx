import { useI18n } from "../i18n";

export function ErrorBanner({ error }: { error: Error & { recovery?: string } }) {
  const { t } = useI18n();
  return (
    <div className="error-banner" role="alert">
      <strong>{error.message}</strong>
      <span>{error.recovery ?? t("error.recovery")}</span>
    </div>
  );
}
