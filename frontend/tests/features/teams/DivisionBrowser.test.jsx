import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import DivisionBrowser from '../../../src/features/teams/DivisionBrowser';

describe('DivisionBrowser', () => {
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
        actionLabel="View Schedule ->"
      />,
    );

    const button = screen.getByRole('button', { name: /Baltimore Ravens/i });
    button.focus();
    await user.keyboard('{Enter}');

    expect(onTeamSelect).toHaveBeenCalledWith('BAL');
  });
});
