import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import App from '../../../src/App';

vi.mock('../../../src/components/player-details/usePlayerDetails', () => ({
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

vi.mock('../../../src/components/player-details/PlayerDetailsModal', () => ({
  default: () => null,
}));

vi.mock('../../../src/components/landing/LandingPage', () => ({
  default: function LandingPageMock({ onNavigate }) {
    return (
      <div>
        <p>Landing Mock</p>
        <button type="button" onClick={() => onNavigate('statistics')}>
          Open Statistics
        </button>
      </div>
    );
  },
}));

vi.mock('../../../src/components/app/AppHeader', () => ({
  default: function AppHeaderMock({ onHome }) {
    return (
      <button type="button" onClick={onHome}>
        Go Home
      </button>
    );
  },
}));

vi.mock('../../../src/components/statistics/Statistics', () => ({
  default: function StatisticsMock() {
    return <div>Statistics View</div>;
  },
}));

vi.mock('../../../src/components/team-browser/Schedules', () => ({
  default: function SchedulesMock() {
    return <div>Schedules View</div>;
  },
}));

vi.mock('../../../src/components/team-browser/DepthCharts', () => ({
  default: function DepthChartsMock() {
    return <div>Depth Charts View</div>;
  },
}));

describe('App navigation', () => {
  it('navigates from landing to statistics and back home', async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText('Landing Mock')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Open Statistics' }));
    expect(await screen.findByText('Statistics View')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Go Home' }));
    await waitFor(() => {
      expect(screen.getByText('Landing Mock')).toBeInTheDocument();
    });
    expect(screen.queryByText('Statistics View')).not.toBeInTheDocument();
  });
});

