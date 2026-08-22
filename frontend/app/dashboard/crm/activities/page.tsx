'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export default function ActivitiesPage() {
  const [filterType, setFilterType] = useState('');

  const { data: activities = [], isLoading } = useQuery({
    queryKey: ['activities'],
    queryFn: () => api.get('/contacts/activities').then(r => r.data).catch(() => []),
  });

  const filteredActivities = filterType
    ? activities.filter((a: any) => a.activity_type === filterType)
    : activities;

  const activityTypes = ['CALL', 'EMAIL', 'MEETING', 'NOTE', 'TASK'];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'CALL': return '📞';
      case 'EMAIL': return '📧';
      case 'MEETING': return '👥';
      case 'NOTE': return '📝';
      case 'TASK': return '✓';
      default: return '📌';
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">Activities</h1>

      <div className="mb-6 flex gap-2 flex-wrap">
        <button
          onClick={() => setFilterType('')}
          className={`px-4 py-2 rounded-lg ${!filterType ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          All
        </button>
        {activityTypes.map(type => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-4 py-2 rounded-lg ${filterType === type ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            {getActivityIcon(type)} {type}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading activities...</div>
      ) : (
        <div className="space-y-4">
          {filteredActivities.map((activity: any) => (
            <div key={activity.id} className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-600">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getActivityIcon(activity.activity_type)}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{activity.title}</h3>
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded">
                      {activity.activity_type}
                    </span>
                  </div>
                  {activity.description && (
                    <p className="text-gray-600 text-sm">{activity.description}</p>
                  )}
                </div>
                <div className="text-right text-sm text-gray-600">
                  {activity.created_at && new Date(activity.created_at).toLocaleDateString()}
                </div>
              </div>
              {activity.duration_seconds && (
                <div className="mt-3 text-sm text-gray-600">
                  Duration: {Math.round(activity.duration_seconds / 60)} mins
                </div>
              )}
            </div>
          ))}
          {filteredActivities.length === 0 && (
            <div className="text-center py-12 text-gray-500">No activities found</div>
          )}
        </div>
      )}
    </div>
  );
}
