function getValueClassName(displayValue, isWinner) {
  return [
    'direct-comparison-value-chip',
    displayValue === '—' ? 'direct-comparison-value-chip--missing' : '',
    isWinner ? 'direct-comparison-value-chip--winner' : '',
  ]
    .filter(Boolean)
    .join(' ');
}

export default function PlayerComparisonValueCell({ displayValue, isWinner }) {
  return (
    <td>
      <span className={getValueClassName(displayValue, isWinner)}>{displayValue}</span>
    </td>
  );
}
