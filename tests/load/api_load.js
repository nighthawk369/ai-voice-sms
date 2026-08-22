/**
 * k6 Load Testing Script
 * Tests API endpoints under load
 * 
 * Run: k6 run tests/load/api_load.js --vus 100 --duration 30s
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';
const SIGNUP_THRESHOLD = 0.95;
const LOGIN_THRESHOLD = 0.95;
const API_THRESHOLD = 0.90;

const signupErrorRate = new Rate('signup_errors');
const loginErrorRate = new Rate('login_errors');
const apiErrorRate = new Rate('api_errors');

const signupDuration = new Trend('signup_duration');
const loginDuration = new Trend('login_duration');
const apiDuration = new Trend('api_duration');

export const options = {
  stages: [
    { duration: '10s', target: 20 },
    { duration: '20s', target: 100 },
    { duration: '10s', target: 50 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'],
    'signup_errors': [`rate<${1 - SIGNUP_THRESHOLD}`],
    'login_errors': [`rate<${1 - LOGIN_THRESHOLD}`],
    'api_errors': [`rate<${1 - API_THRESHOLD}`],
  },
};

export default function() {
  let token = '';

  group('Authentication', function() {
    const email = `user${Math.random() * 1000}@example.com`;
    const password = 'TestPassword123!';

    // Signup
    const signupRes = http.post(`${BASE_URL}/api/v1/auth/signup`, JSON.stringify({
      email: email,
      password: password,
      business_type: 'hvac_contractor'
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    check(signupRes, {
      'signup status is 201': (r) => r.status === 201,
      'signup response has user id': (r) => r.json('id') !== null,
    }) || signupErrorRate.add(1);
    signupDuration.add(signupRes.timings.duration);

    // Login
    const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
      email: email,
      password: password,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'login response has token': (r) => r.json('access_token') !== null,
    }) || loginErrorRate.add(1);
    loginDuration.add(loginRes.timings.duration);

    token = loginRes.json('access_token');
  });

  sleep(1);

  group('CRM Operations', function() {
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };

    // Create Contact
    const contactRes = http.post(`${BASE_URL}/api/v1/contacts`, JSON.stringify({
      first_name: 'John',
      last_name: 'Doe',
      email: `john${Math.random() * 1000}@example.com`,
      phone: '+13125551234'
    }), { headers });

    const contactId = contactRes.json('id');
    check(contactRes, {
      'create contact status is 201': (r) => r.status === 201,
      'contact has id': (r) => r.json('id') !== null,
    }) || apiErrorRate.add(1);
    apiDuration.add(contactRes.timings.duration);

    // Get Contacts
    const getContactsRes = http.get(`${BASE_URL}/api/v1/contacts`, { headers });
    check(getContactsRes, {
      'get contacts status is 200': (r) => r.status === 200,
      'contacts is array': (r) => Array.isArray(r.json()),
    }) || apiErrorRate.add(1);
    apiDuration.add(getContactsRes.timings.duration);

    // Get Single Contact
    const getSingleRes = http.get(`${BASE_URL}/api/v1/contacts/${contactId}`, { headers });
    check(getSingleRes, {
      'get single contact status is 200': (r) => r.status === 200,
      'contact first name is John': (r) => r.json('first_name') === 'John',
    }) || apiErrorRate.add(1);
    apiDuration.add(getSingleRes.timings.duration);

    // Get Business Types
    const btRes = http.get(`${BASE_URL}/api/v1/business-types`);
    check(btRes, {
      'business types status is 200': (r) => r.status === 200,
      'has business types': (r) => r.json('business_types').length > 0,
    }) || apiErrorRate.add(1);
    apiDuration.add(btRes.timings.duration);
  });

  sleep(Math.random() * 3);
}

export function teardown(data) {
  console.log('Load test completed');
  console.log(`Final error rate: ${apiErrorRate.value}`);
}
