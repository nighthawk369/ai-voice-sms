'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export default function DealsPage() {
  const [filterStatus, setFilterStatus] = useState('');

  const { data: deals = [], isLoading } = useQuery({
    queryKey: ['deals'],
    queryFn: () => api.get('/deals').then(r => r.data),
  });

  const filteredDeals = filterStatus
    ? deals.filter((d: any) => d.deal_status === filterStatus)
    : deals;

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Deals</h1>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
          + New Deal
        </button>
      </div>

      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setFilterStatus('')}
          className={`px-4 py-2 rounded-lg ${!filterStatus ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          All
        </button>
        <button
          onClick={() => setFilterStatus('OPEN')}
          className={`px-4 py-2 rounded-lg ${filterStatus === 'OPEN' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Open
        </button>
        <button
          onClick={() => setFilterStatus('WON')}
          className={`px-4 py-2 rounded-lg ${filterStatus === 'WON' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
        >
          Won
        </button>
        <button
          onClick={() => setFilterStatus('LOST')}
          className={`px-4 py-2 rounded-lg ${filterStatus === 'LOST' ? 'bg-red-600 text-white' : 'bg-gray-200'}`}
        >
          Lost
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading deals...</div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredDeals.map((deal: any) => (
            <div key={deal.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{deal.name}</h3>
                  <p className="text-gray-600 text-sm mt-1">{deal.description || 'No description'}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  deal.deal_status === 'WON' ? 'bg-green-100 text-green-800' :
                  deal.deal_status === 'LOST' ? 'bg-red-100 text-red-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {deal.deal_status}
                </span>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Amount</p>
                  <p className="font-semibold text-gray-900">${deal.amount ? deal.amount.toLocaleString() : '0'}</p>
                </div>
                <div>
                  <p className="text-gray-600">Probability</p>
                  <p className="font-semibold text-gray-900">{deal.probability}%</p>
                </div>
                <div>
                  <p className="text-gray-600">Stage</p>
                  <p className="font-semibold text-gray-900">{deal.stage}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
