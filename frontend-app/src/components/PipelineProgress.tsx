export const pipelineSteps = [
  "Classifying intent...",
  "Scoring urgency...",
  "Retrieving policies...",
  "Drafting response locally...",
  "Validating draft safety...",
  "Saving workflow state..."
];

export function PipelineProgress({ activeStep, running }: { activeStep: number; running: boolean }) {
  return (
    <ol className="pipeline" aria-label="Pipeline progress" aria-live="polite">
      {pipelineSteps.map((step, index) => (
        <li key={step} className={index < activeStep ? "done" : index === activeStep && running ? "active" : ""}>
          <span>{index < activeStep ? "Done" : index === activeStep && running ? "Running" : "Waiting"}</span>
          {step}
        </li>
      ))}
    </ol>
  );
}
