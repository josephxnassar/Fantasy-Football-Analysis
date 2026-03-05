import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import DivisionBrowser from '../../../src/components/DivisionBrowser';
import TeamSearch from '../../../src/components/TeamSearch';
import PlayerCard from '../../../src/components/common/PlayerCard';

describe('interactive frontend controls', () => {
  it('renders player cards as keyboard-accessible buttons', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();

    render(
      <PlayerCard
        player={{ name: 'Christian McCaffrey', team: 'SF', position: 'RB', age: 29 }}
        onPlayerClick={onPlayerClick}
      />
    );

    const button = screen.getByRole('button', { name: /Christian McCaffrey/i });
    await user.tab();
    expect(button).toHaveFocus();
    await user.keyboard('{Enter}');

    expect(onPlayerClick).toHaveBeenCalledWith(
      'Christian McCaffrey',
      expect.objectContaining({ name: 'Christian McCaffrey' })
    );
  });

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

  it('renders division team cards as buttons', async () => {
    const user = userEvent.setup();
    const onTeamSelect = vi.fn();

    render(
      <DivisionBrowser
        divisions={{ AFC: { North: ['BAL'], East: ['BUF'] }, NFC: { North: ['GB'] } }}
        teamNames={{ BAL: 'Baltimore Ravens', BUF: 'Buffalo Bills', GB: 'Green Bay Packers' }}
        loading={false}
        error={null}
        onTeamSelect={onTeamSelect}
        actionLabel="View Schedule →"
      />
    );

    const button = screen.getByRole('button', { name: /Baltimore Ravens/i });
    button.focus();
    await user.keyboard('{Enter}');

    expect(onTeamSelect).toHaveBeenCalledWith('BAL');
  });
});
