import { Children, cloneElement, isValidElement } from 'react';

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import SeasonTrendsChart from '../../../../src/features/statistics/charts/SeasonTrendsChart';

vi.mock('recharts', () => {
  const Passthrough = ({ children }) => <div>{children}</div>;
  return {
    ResponsiveContainer: Passthrough,
    XAxis: () => null,
    YAxis: () => null,
    Tooltip: () => null,
    LineChart: ({ data = [], children }) => (
      <div>
        {Children.map(children, (child) =>
          isValidElement(child) ? cloneElement(child, { __chartData: data }) : child
        )}
      </div>
    ),
    Line: ({ __chartData = [], dot, activeDot }) => (
      <div>
        {__chartData.map((payload, index) => (
          <div key={`${payload.season}-${index}`}>
            {(() => {
              if (typeof dot !== 'function') return null;
              const rendered = dot({ cx: 20 + index, cy: 20, payload });
              const onClick = rendered?.props?.onClick;
              if (!onClick) return null;
              return (
                <button type="button" onClick={onClick}>
                  Dot {payload.season}
                </button>
              );
            })()}
            {(() => {
              if (typeof activeDot !== 'function') return null;
              const rendered = activeDot({ cx: 40 + index, cy: 40, payload });
              const onClick = rendered?.props?.onClick;
              if (!onClick) return null;
              return (
                <button type="button" onClick={onClick}>
                  Active Dot {payload.season}
                </button>
              );
            })()}
          </div>
        ))}
      </div>
    ),
  };
});

describe('SeasonTrendsChart', () => {
  it('shows empty-state message when player or data is missing', () => {
    const { rerender } = render(<SeasonTrendsChart data={[]} playerName="Josh Allen" statLabel="PPR Pts" />);
    expect(
      screen.getByText('No multi-season trend data available for this selection.')
    ).toBeInTheDocument();

    rerender(<SeasonTrendsChart data={[{ season: 2025, value: 320.4 }]} playerName="" statLabel="PPR Pts" />);
    expect(
      screen.getByText('No multi-season trend data available for this selection.')
    ).toBeInTheDocument();
  });

  it('opens player modal at clicked season when trend point is clicked', async () => {
    const user = userEvent.setup();
    const onPlayerSeasonClick = vi.fn();
    render(
      <SeasonTrendsChart
        data={[
          { season: 2024, value: 301.2 },
          { season: 2025, value: 329.8 },
        ]}
        playerName="Josh Allen"
        statLabel="PPR Pts"
        onPlayerSeasonClick={onPlayerSeasonClick}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Dot 2024' }));

    expect(onPlayerSeasonClick).toHaveBeenCalledWith('Josh Allen', 2024);
  });

  it('falls back to player click when season callback is unavailable', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();
    render(
      <SeasonTrendsChart
        data={[{ season: 2025, value: 329.8 }]}
        playerName="Josh Allen"
        statLabel="PPR Pts"
        onPlayerClick={onPlayerClick}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Dot 2025' }));

    expect(onPlayerClick).toHaveBeenCalledWith('Josh Allen');
  });

  it('keeps caption player link clickable', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();
    render(
      <SeasonTrendsChart
        data={[{ season: 2025, value: 329.8 }]}
        playerName="Josh Allen"
        statLabel="PPR Pts"
        onPlayerClick={onPlayerClick}
      />
    );

    await user.click(screen.getByRole('button', { name: 'Josh Allen' }));
    expect(onPlayerClick).toHaveBeenCalledWith('Josh Allen');
  });
});
