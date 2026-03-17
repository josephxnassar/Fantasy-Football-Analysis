import { Children, cloneElement, isValidElement } from 'react';

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import LeaderboardChart from '../../../../src/features/statistics/charts/LeaderboardChart';

vi.mock('recharts', () => {
  const Passthrough = ({ children }) => <div>{children}</div>;
  return {
    ResponsiveContainer: Passthrough,
    CartesianGrid: () => null,
    XAxis: () => null,
    Tooltip: () => null,
    Rectangle: ({ onClick }) => (
      <button type="button" onClick={onClick}>
        Bar
      </button>
    ),
    BarChart: ({ data = [], children }) => (
      <div>
        {Children.map(children, (child) =>
          isValidElement(child) ? cloneElement(child, { __chartData: data }) : child
        )}
      </div>
    ),
    YAxis: ({ __chartData = [], onClick }) => (
      <div>
        {__chartData.map((row, index) => (
          <button key={`${row.name}-${index}`} type="button" onClick={() => onClick?.({ value: row.name })}>
            {row.name}
          </button>
        ))}
      </div>
    ),
    Bar: ({ __chartData = [], shape }) => (
      <div>
        {__chartData.map((payload, index) => (
          <div key={`${payload.name}-${index}`}>
            {typeof shape === 'function'
              ? shape({ payload, index, x: 0, y: 0, width: 10, height: 10 })
              : null}
          </div>
        ))}
      </div>
    ),
  };
});

describe('LeaderboardChart', () => {
  it('shows empty-state message when no chart rows exist', () => {
    render(<LeaderboardChart data={[]} />);
    expect(screen.getByText('No data available for the selected stat.')).toBeInTheDocument();
  });

  it('opens player modal at selected season when label is clicked', async () => {
    const user = userEvent.setup();
    const onPlayerSeasonClick = vi.fn();
    const onPlayerClick = vi.fn();
    render(
      <LeaderboardChart
        data={[
          { name: 'Josh Allen', value: 380.4 },
          { name: 'Lamar Jackson', value: 362.1 },
        ]}
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
      <LeaderboardChart
        data={[
          { name: 'Josh Allen', value: 380.4 },
          { name: 'Lamar Jackson', value: 362.1 },
        ]}
        season={2025}
        onPlayerClick={onPlayerClick}
      />
    );

    await user.click(screen.getAllByRole('button', { name: 'Bar' })[0]);

    expect(onPlayerClick).toHaveBeenCalledWith('Josh Allen');
  });
});
