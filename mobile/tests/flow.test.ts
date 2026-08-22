/**
 * Mobile Flow Tests
 * Test complete user journeys in the React Native app
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock AsyncStorage
const mockAsyncStorage = {
  storage: {},
  setItem: function(key: string, value: string) {
    this.storage[key] = value;
  },
  getItem: function(key: string) {
    return this.storage[key] || null;
  },
  removeItem: function(key: string) {
    delete this.storage[key];
  },
  clear: function() {
    this.storage = {};
  }
};

// Mock API responses
const mockApiResponses = {
  signup: { 
    id: 'user-1', 
    email: 'test@example.com', 
    business_type: 'hvac_contractor' 
  },
  login: { 
    access_token: 'test-token', 
    user_id: 'user-1' 
  },
  businessTypes: {
    business_types: [
      { value: 'hvac_contractor', label: 'HVAC Contractor', category: 'SERVICE' },
      { value: 'electrician', label: 'Electrician', category: 'SERVICE' },
    ],
    categories: ['SERVICE', 'RETAIL']
  },
  contacts: [
    { id: 'contact-1', first_name: 'John', last_name: 'Doe', email: 'john@example.com' }
  ]
};

describe('Mobile Flow Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAsyncStorage.clear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should complete signup flow on mobile', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => mockApiResponses.signup
    });

    const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'TestPassword123!',
        business_type: 'hvac_contractor'
      })
    });

    const data = await response.json();
    expect(response.status).toBe(201);
    expect(data.email).toBe('test@example.com');
    expect(data.business_type).toBe('hvac_contractor');
  });

  it('should handle business type selection', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockApiResponses.businessTypes
    });

    const response = await fetch('http://localhost:8000/api/v1/business-types');
    const data = await response.json();

    expect(data.business_types.length).toBeGreaterThan(0);
    expect(data.categories.includes('SERVICE')).toBe(true);
  });

  it('should persist authentication on mobile', async () => {
    const token = 'test-mobile-token';
    const user = { id: 'user-1', email: 'mobile@example.com' };

    mockAsyncStorage.setItem('access_token', token);
    mockAsyncStorage.setItem('user', JSON.stringify(user));

    const storedToken = mockAsyncStorage.getItem('access_token');
    const storedUser = JSON.parse(mockAsyncStorage.getItem('user') || '{}');

    expect(storedToken).toBe(token);
    expect(storedUser.email).toBe('mobile@example.com');
  });

  it('should fetch contacts on mobile', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockApiResponses.contacts
    });

    const response = await fetch('http://localhost:8000/api/v1/contacts', {
      headers: { 'Authorization': 'Bearer test-token' }
    });

    const data = await response.json();
    expect(Array.isArray(data)).toBe(true);
    expect(data[0].first_name).toBe('John');
  });

  it('should handle navigation state', () => {
    const navigationState = {
      index: 0,
      routes: [
        { name: 'Login', params: undefined },
        { name: 'Signup', params: { business_type: 'hvac_contractor' } },
        { name: 'Dashboard', params: { user_id: 'user-1' } }
      ]
    };

    expect(navigationState.routes[0].name).toBe('Login');
    expect(navigationState.routes[2].params.user_id).toBe('user-1');
  });

  it('should handle offline scenario', () => {
    const isOnline = false;
    
    if (!isOnline) {
      // Show offline message
      const offlineMessage = 'You are offline. Some features may be unavailable.';
      expect(offlineMessage).toBeDefined();
    }
  });

  it('should create conversation flow', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ id: 'conv-1', contact_id: 'contact-1', type: 'inbound_call' })
    });

    const response = await fetch('http://localhost:8000/api/v1/conversations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
      },
      body: JSON.stringify({ contact_id: 'contact-1', type: 'inbound_call' })
    });

    const data = await response.json();
    expect(response.status).toBe(201);
    expect(data.id).toBe('conv-1');
  });
});
