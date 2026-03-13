import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import AverageVsUpsideChart from '../../../../src/components/charts/AverageVsUpsideChart';

vi.mock('recharts', () => {
  const Passthrough = ({ children }) => <div>{children}</div>;
  return {
    ResponsiveContainer: Passthrough,
    ScatterChart: Passthrough,
    XAxis: () => null,
    YAxis: () => null,
    ZAxis: () => null,
    Tooltip: () => null,
    Scatter: ({ data = [], onClick }) => (
      <div>
        {data.map((point, index) => (
          <button
            key={`${point.name}-${index}`}
            type="button"
            onClick={() => onClick?.({ payload: point })}
          >
            {point.name}
          </button>
        ))}
      </div>
    ),
  };
});

describe('AverageVsUpsideChart', () => {
  it('shows empty-state message when data is missing', () => {
    render(<AverageVsUpsideChart data={[]} season={2025} />);
    expect(screen.getByText('No weekly data available for this season.')).toBeInTheDocument();
  });

  it('opens player modal at selected season when point is clicked', async () => {
    const user = userEvent.setup();
    const onPlayerSeasonClick = vi.fn();
    const onPlayerClick = vi.fn();
    render(
      <AverageVsUpsideChart
        data={[{ name: 'Josh Allen', avg_fp_ppr: 24.2, ceiling_fp_ppr: 36.8, volatility_fp_ppr: 5.9, games: 17 }]}
        season={2025}
        onPlayerClick={onPlayerClick}
        onPlayerSeasonClick={onPlayerSeasonClick}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));

    expect(onPlayerSeasonClick).toHaveBeenCalledWith('Josh Allen', 2025);
    expect(onPlayerClick).not.toHaveBeenCalled();
  });

  it('falls back to basic player click when season callback is unavailable', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();
    render(
      <AverageVsUpsideChart
        data={[{ name: 'Lamar Jackson', avg_fp_ppr: 23.1, ceiling_fp_ppr: 34.4, volatility_fp_ppr: 6.2, games: 16 }]}
        season={undefined}
        onPlayerClick={onPlayerClick}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Lamar Jackson' }));

    expect(onPlayerClick).toHaveBeenCalledWith('Lamar Jackson');
  });
});
