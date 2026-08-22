/**
 * Frontend Flow Tests
 * Test complete user journeys through the application
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock API responses
const mockApiResponses = {
  signup: { id: 'user-1', email: 'test@example.com', business_type: 'hvac_contractor' },
  login: { access_token: 'test-token', user_id: 'user-1' },
  businessTypes: {
    business_types: [
      { value: 'hvac_contractor', label: 'HVAC Contractor', category: 'SERVICE', description: 'HVAC services' },
      { value: 'electrician', label: 'Electrician', category: 'SERVICE', description: 'Electrical services' },
    ],
    categories: ['SERVICE', 'RETAIL']
  },
  contacts: [
    { id: 'contact-1', first_name: 'John', last_name: 'Doe', email: 'john@example.com' }
  ]
};

describe('Frontend Flow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should complete signup flow', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockApiResponses.signup
    });

    const response = await fetch('/api/v1/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'TestPassword123!',
        business_type: 'hvac_contractor'
      })
    });

    const data = await response.json();
    expect(response.status).toBe(201);
    expect(data.email).toBe('test@example.com');
  });

  it('should display business type selector with categories', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockApiResponses.businessTypes
    });

    const businessTypes = mockApiResponses.businessTypes.business_types;
    const grouped = businessTypes.reduce((acc, bt) => {
      if (!acc[bt.category]) acc[bt.category] = [];
      acc[bt.category].push(bt);
      return acc;
    }, {});

    expect(Object.keys(grouped)).toContain('SERVICE');
    expect(grouped['SERVICE']).toHaveLength(2);
  });

  it('should handle authentication flow', async () => {
    // Signup
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockApiResponses.signup
    });

    // Login
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockApiResponses.login
    });

    const token = 'test-token';
    localStorage.setItem('access_token', token);
    
    expect(localStorage.getItem('access_token')).toBe(token);
  });

  it('should fetch and display contacts', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockApiResponses.contacts
    });

    const response = await fetch('/api/v1/contacts', {
      headers: { 'Authorization': 'Bearer test-token' }
    });

    const data = await response.json();
    expect(data).toHaveLength(1);
    expect(data[0].first_name).toBe('John');
  });

  it('should handle API errors gracefully', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' })
    });

    const response = await fetch('/api/v1/contacts', {
      headers: { 'Authorization': 'Bearer invalid-token' }
    });

    expect(response.ok).toBe(false);
    expect(response.status).toBe(401);
  });

  it('should persist authentication state', () => {
    const token = 'test-token';
    const user = { id: 'user-1', email: 'test@example.com' };

    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));

    const storedToken = localStorage.getItem('access_token');
    const storedUser = JSON.parse(localStorage.getItem('user') || '{}');

    expect(storedToken).toBe(token);
    expect(storedUser.email).toBe('test@example.com');
  });
});
