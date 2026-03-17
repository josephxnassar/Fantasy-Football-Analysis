import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import TeamScheduleModal from '../../../src/features/teams/TeamScheduleModal';
import { useTeamModalData } from '../../../src/shared/hooks/useTeamModalData';

vi.mock('../../../src/shared/hooks/useTeamModalData', () => ({
  useTeamModalData: vi.fn(),
}));

const SCHEDULE_MOCK = {
  team: 'BUF',
  team_name: 'Buffalo Bills',
  season: 2025,
  available_seasons: [2025, 2024],
  bye_week: 7,
  schedule: [
    {
      week: 1,
      opponent: 'KC',
      home_away: 'HOME',
      winner: 'BUF',
      team_score: 31,
      opponent_score: 28,
    },
    {
      week: 2,
      opponent: 'BYE',
      home_away: null,
      winner: null,
      team_score: null,
      opponent_score: null,
    },
  ],
};

describe('TeamScheduleModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTeamModalData.mockReturnValue({
      data: SCHEDULE_MOCK,
      loading: false,
      error: null,
    });
  });

  it('expands game details and does not expand bye weeks', async () => {
    const user = userEvent.setup();

    render(<TeamScheduleModal team="BUF" onClose={vi.fn()} />);

    expect(screen.queryByText('Winner: BUF')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Week 1/i }));
    expect(screen.getByText('Winner: BUF')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Week 2/i }));
    expect(screen.getByText('Winner: BUF')).toBeInTheDocument();
  });
});
