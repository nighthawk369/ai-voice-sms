'use client';

import { useAuth } from '@/lib/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">AI Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={logout}
                className="text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 p-4">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-gray-900">Welcome, {user.first_name || user.email}!</h2>

              <p className="text-gray-600">
                You're successfully logged into the AI Platform. This is the dashboard home page.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold text-gray-900 mb-2">Quick Links</h3>
                  <ul className="space-y-2">
                    <li>
                      <Link href="/dashboard/settings" className="text-blue-600 hover:text-blue-500">
                        → Settings
                      </Link>
                    </li>
                    <li>
                      <Link href="/dashboard/admin" className="text-blue-600 hover:text-blue-500">
                        → Admin Panel
                      </Link>
                    </li>
                  </ul>
                </div>

                <div className="bg-white p-4 rounded-lg shadow">
                  <h3 className="font-semibold text-gray-900 mb-2">Account Info</h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Role: <span className="font-medium">{user.role}</span></p>
                    <p>Email: <span className="font-medium">{user.email}</span></p>
                    <p>Status: <span className="font-medium">{user.is_active ? 'Active' : 'Inactive'}</span></p>
                  </div>
                </div>
              </div>

              <div className="pt-4 text-sm text-gray-500">
                📖 See <span className="font-mono">MASTER_SPECIFICATION.md</span> for complete documentation.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
