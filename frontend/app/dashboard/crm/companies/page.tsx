'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function CompaniesPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: companies = [], isLoading, error } = useQuery({
    queryKey: ['companies'],
    queryFn: () => api.get('/companies').then(r => r.data),
  });

  const filteredCompanies = companies.filter((c: any) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.industry && c.industry.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Companies</h1>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
          + New Company
        </button>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search companies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading companies...</div>
      ) : error ? (
        <div className="text-red-600">Error loading companies</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Industry</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Website</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCompanies.map((company: any) => (
                <tr key={company.id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium">{company.name}</td>
                  <td className="px-6 py-4">{company.industry || '-'}</td>
                  <td className="px-6 py-4">
                    {company.website ? (
                      <a href={company.website} target="_blank" className="text-blue-600 hover:underline">
                        {company.website}
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {company.company_status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <Link href={`/dashboard/crm/companies/${company.id}`} className="text-blue-600 hover:underline">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredCompanies.length === 0 && (
            <div className="text-center py-8 text-gray-500">No companies found</div>
          )}
        </div>
      )}
    </div>
  );
}
