import { useI18n, type TranslationKey } from "../i18n";

export const pipelineStepKeys: TranslationKey[] = ["pipeline.classify", "pipeline.urgency", "pipeline.policies", "pipeline.draft", "pipeline.safety", "pipeline.save"];

export function PipelineProgress({ activeStep, running }: { activeStep: number; running: boolean }) {
  const { t } = useI18n();
  return (
    <ol className="pipeline" aria-label={t("pipeline.aria")} aria-live="polite">
      {pipelineStepKeys.map((step, index) => (
        <li key={step} className={index < activeStep ? "done" : index === activeStep && running ? "active" : ""}>
          <span>{index < activeStep ? t("pipeline.done") : index === activeStep && running ? t("pipeline.running") : t("pipeline.waiting")}</span>
          {t(step)}
        </li>
      ))}
    </ol>
  );
}
