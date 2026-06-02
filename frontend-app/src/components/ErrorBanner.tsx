export function ErrorBanner({ error }: { error: Error & { recovery?: string } }) {
  return (
    <div className="error-banner" role="alert">
      <strong>{error.message}</strong>
      <span>{error.recovery ?? "Check the local runtime status, then retry."}</span>
    </div>
  );
}
