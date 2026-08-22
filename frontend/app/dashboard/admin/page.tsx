'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/useAuth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AdminPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
    if (!isLoading && user && !['OWNER', 'ADMIN'].includes(user.role)) {
      router.push('/dashboard');
    }
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || !user || !['OWNER', 'ADMIN'].includes(user.role)) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                ← Dashboard
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">Admin Panel</h1>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Organizations */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Organizations</h3>
            <p className="text-gray-600 text-sm mb-4">Manage organizations and tenants</p>
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50" disabled>
              View Organizations (Coming Soon)
            </button>
          </div>

          {/* Users */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Users</h3>
            <p className="text-gray-600 text-sm mb-4">Manage users and permissions</p>
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50" disabled>
              View Users (Coming Soon)
            </button>
          </div>

          {/* System Health */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
            <p className="text-gray-600 text-sm mb-4">Monitor service status</p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Database</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">✓ Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Redis</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">✓ Healthy</span>
              </div>
              <div className="flex items-center justify-between">
                <span>API</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">✓ Healthy</span>
              </div>
            </div>
          </div>

          {/* Feature Flags */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Feature Flags</h3>
            <p className="text-gray-600 text-sm mb-4">Control feature availability</p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Voice AI</span>
                <input type="checkbox" defaultChecked disabled className="w-4 h-4" />
              </div>
              <div className="flex items-center justify-between">
                <span>SMS AI</span>
                <input type="checkbox" defaultChecked disabled className="w-4 h-4" />
              </div>
              <div className="flex items-center justify-between">
                <span>Private AI</span>
                <input type="checkbox" defaultChecked disabled className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
