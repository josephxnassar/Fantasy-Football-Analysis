import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import TeamSearch from '../../../src/components/team-browser/TeamSearch';

describe('TeamSearch', () => {
  it('renders searched teams as buttons', async () => {
    const user = userEvent.setup();
    const onTeamSelect = vi.fn();

    render(
      <TeamSearch
        allTeams={['KC', 'BUF']}
        teamNames={{ KC: 'Kansas City Chiefs', BUF: 'Buffalo Bills' }}
        loading={false}
        error={null}
        onTeamSelect={onTeamSelect}
      />
    );

    const button = screen.getByRole('button', { name: /Kansas City Chiefs/i });
    button.focus();
    await user.keyboard('{Enter}');

    expect(onTeamSelect).toHaveBeenCalledWith('KC');
  });
});
