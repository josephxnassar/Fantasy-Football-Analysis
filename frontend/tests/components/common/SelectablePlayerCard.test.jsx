import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import SelectablePlayerCard from '../../../src/components/common/SelectablePlayerCard';

describe('SelectablePlayerCard', () => {
  it('renders as a keyboard-accessible button', async () => {
    const user = userEvent.setup();
    const onPlayerClick = vi.fn();

    render(
      <SelectablePlayerCard
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
});
