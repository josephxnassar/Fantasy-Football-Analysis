import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import PlayerDetailsModal from '../../../../src/features/statistics/player-details/PlayerDetailsModal';
import { useTeamModalData } from '../../../../src/shared/hooks/useTeamModalData';

vi.mock('../../../../src/shared/hooks/useTeamModalData', () => ({
  useTeamModalData: vi.fn(),
}));

vi.mock('../../../../src/features/statistics/player-details/PlayerHeader', () => ({
  default: () => <div>Player Header</div>,
}));

vi.mock('../../../../src/features/statistics/player-details/PlayerDepthChartTab', () => ({
  default: () => <div>Depth Chart View</div>,
}));

describe('PlayerDetailsModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTeamModalData.mockReturnValue({
      data: null,
      loading: false,
      error: null,
    });
  });

  it('loads team depth chart data only after opening the depth chart tab', async () => {
    const user = userEvent.setup();

    render(
      <PlayerDetailsModal
        playerDetails={{ name: 'Patrick Mahomes', team: 'KC' }}
        loading={false}
        error={null}
        onClose={vi.fn()}
        availableSeasons={[2025]}
        currentSeason={2025}
        onSeasonChange={vi.fn()}
      />
    );

    expect(useTeamModalData).toHaveBeenCalledWith(
      null,
      expect.any(Function),
      'Failed to load depth chart'
    );

    await user.click(screen.getByRole('button', { name: 'Depth Chart' }));

    expect(useTeamModalData).toHaveBeenLastCalledWith(
      'KC',
      expect.any(Function),
      'Failed to load depth chart'
    );
  });
});
