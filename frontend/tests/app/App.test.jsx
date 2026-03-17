import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import App from '../../src/app/App';

vi.mock('../../src/features/statistics/player-details/usePlayerDetails', () => ({
  usePlayerDetails: () => ({
    playerDetails: null,
    loadingDetails: false,
    detailsError: null,
    availableSeasons: [],
    currentSeason: null,
    handlePlayerClick: vi.fn(),
    handlePlayerSeasonClick: vi.fn(),
    handleSeasonChange: vi.fn(),
    closeDetails: vi.fn(),
  }),
}));

vi.mock('../../src/features/statistics/player-details/PlayerDetailsModal', () => ({
  default: () => null,
}));

vi.mock('../../src/features/home/HomePage', () => ({
  default: function HomePageMock({ onNavigate }) {
    return (
      <div>
        <p>Home Mock</p>
        <button type="button" onClick={() => onNavigate('statistics')}>
          Open Statistics
        </button>
      </div>
    );
  },
}));

vi.mock('../../src/app/shell/AppHeader', () => ({
  default: function AppHeaderMock({ onHome }) {
    return (
      <button type="button" onClick={onHome}>
        Go Home
      </button>
    );
  },
}));

vi.mock('../../src/features/statistics/Statistics', () => ({
  default: function StatisticsMock() {
    return <div>Statistics View</div>;
  },
}));

vi.mock('../../src/features/teams/Schedules', () => ({
  default: function SchedulesMock() {
    return <div>Schedules View</div>;
  },
}));

vi.mock('../../src/features/teams/DepthCharts', () => ({
  default: function DepthChartsMock() {
    return <div>Depth Charts View</div>;
  },
}));

describe('App navigation', () => {
  it('navigates from home to statistics and back home', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText('Home Mock')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Open Statistics' }));
    expect(await screen.findByText('Statistics View')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Go Home' }));
    await waitFor(() => {
      expect(screen.getByText('Home Mock')).toBeInTheDocument();
    });
    expect(screen.queryByText('Statistics View')).not.toBeInTheDocument();
  });
});
