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
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">🚀 AI Platform</h1>
            <div className="flex items-center space-x-6">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome, {user.first_name || 'User'}! 👋
          </h2>
          <p className="text-gray-600">Manage your CRM, AI conversations, and integrations</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <StatCard title="Contacts" value="0" icon="👥" href="/dashboard/crm/contacts" />
          <StatCard title="Companies" value="0" icon="🏢" href="/dashboard/crm/companies" />
          <StatCard title="Deals" value="0" icon="💼" href="/dashboard/crm/deals" />
          <StatCard title="Calls" value="0" icon="📞" href="/dashboard/conversations" />
        </div>

        {/* CRM Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">CRM Management</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <NavigationCard
              href="/dashboard/crm/contacts"
              title="👥 Contacts"
              description="Manage customers and leads"
            />
            <NavigationCard
              href="/dashboard/crm/companies"
              title="🏢 Companies"
              description="Track accounts and organizations"
            />
            <NavigationCard
              href="/dashboard/crm/deals"
              title="💼 Deals"
              description="Manage sales opportunities"
            />
            <NavigationCard
              href="/dashboard/crm/activities"
              title="📅 Activities"
              description="Call logs, emails, meetings"
            />
            <NavigationCard
              href="/dashboard/workflows"
              title="⚙️ Workflows"
              description="Automate business processes"
            />
            <NavigationCard
              href="/dashboard/conversations"
              title="🎙️ Conversations"
              description="AI voice and SMS logs"
            />
          </div>
        </div>

        {/* Integration Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Integrations</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <NavigationCard
              href="/dashboard/integrations"
              title="🔗 Integrations"
              description="Connect external services"
            />
            <NavigationCard
              href="/dashboard/settings"
              title="⚙️ Settings"
              description="Account & organization settings"
            />
            <NavigationCard
              href="/dashboard/admin"
              title="👨‍💼 Admin"
              description="Admin controls and users"
            />
          </div>
        </div>

        {/* User Info Card */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Account</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Name</p>
              <p className="font-medium text-gray-900">
                {user.first_name || 'User'} {user.last_name || ''}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Email</p>
              <p className="font-medium text-gray-900">{user.email}</p>
            </div>
            <div>
              <p className="text-gray-600">Role</p>
              <p className="font-medium text-gray-900">{user.role}</p>
            </div>
            <div>
              <p className="text-gray-600">Status</p>
              <p className="font-medium text-green-600">{user.is_active ? 'Active' : 'Inactive'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, href }: any) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer">
        <div className="text-3xl mb-3">{icon}</div>
        <p className="text-gray-600 text-sm mb-1">{title}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
    </Link>
  );
}

function NavigationCard({ href, title, description }: any) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg hover:scale-105 transition cursor-pointer">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">{title}</h4>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </Link>
  );
}
