import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';

import ErrorBoundary from '../../../../src/components/common/ErrorBoundary';

function MaybeCrash({ shouldCrash }) {
  if (shouldCrash) {
    throw new Error('boom');
  }
  return <div>Healthy child</div>;
}

describe('ErrorBoundary', () => {
  let suppressWindowError;

  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    suppressWindowError = (event) => event.preventDefault();
    window.addEventListener('error', suppressWindowError);
  });

  afterEach(() => {
    window.removeEventListener('error', suppressWindowError);
  });

  it('renders child content when no error occurs', () => {
    render(
      <ErrorBoundary>
        <MaybeCrash shouldCrash={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Healthy child')).toBeInTheDocument();
  });

  it('renders fallback content when a child throws', () => {
    render(
      <ErrorBoundary>
        <MaybeCrash shouldCrash />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reset' })).toBeInTheDocument();
  });

  it('recovers when resetKey changes and children are valid', () => {
    const { rerender } = render(
      <ErrorBoundary resetKey="one">
        <MaybeCrash shouldCrash />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong.')).toBeInTheDocument();

    rerender(
      <ErrorBoundary resetKey="two">
        <MaybeCrash shouldCrash={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Healthy child')).toBeInTheDocument();
  });
});
