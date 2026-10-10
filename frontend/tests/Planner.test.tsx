import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Planner from '../src/components/Planner';

describe('Planner Component Offline Resilience', () => {
  it('disables voice input when offline', () => {
    // Mock navigator.onLine = false
    vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false);
    
    render(<Planner onRouteFound={() => {}} />);
    
    // Find voice button by title or aria-label
    const voiceButton = screen.getByLabelText('Voice input');
    
    // Check if it has disabled attribute and disabled class
    expect(voiceButton).toHaveProperty('disabled', true);
    expect(voiceButton.className).toContain('cursor-not-allowed');
  });

  it('renders quick chips for multi-modal PS-08 trips', () => {
    render(<Planner onRouteFound={() => {}} />);
    
    // Ensure the new chips exist
    expect(screen.getByText('Sabarmati -> BRTS Hub')).toBeDefined();
    expect(screen.getByText('Paldi -> AMTS')).toBeDefined();
  });
});
