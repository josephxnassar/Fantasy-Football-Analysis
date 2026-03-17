/**
 * File overview: Component for Weight Scale within the rankings feature.
 */

import { WEIGHT_LABELS, WEIGHT_STEPS } from './rankingsHelpers';

export default function WeightScale({ value, onChange, compact = false, ariaLabel }) {
  return (
    <div className={`weight-scale ${compact ? 'compact' : ''}`} role="group" aria-label={ariaLabel}>
      {WEIGHT_STEPS.map((step) => (
        <button
          key={step}
          type="button"
          className={`weight-scale-button ${value === step ? 'active' : ''}`}
          onClick={() => onChange(step)}
          aria-pressed={value === step}
          title={`${WEIGHT_LABELS[String(step)]} (${step > 0 ? `+${step}` : step})`}
        >
          {compact ? step : WEIGHT_LABELS[String(step)]}
        </button>
      ))}
    </div>
  );
}
