/**
 * Reusable data table component with sorting, filtering, and pagination
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  total: number;
  skip: number;
  limit: number;
  hasMore: boolean;
  isLoading: boolean;
  onPageChange: (skip: number) => void;
  onSortChange?: (sortBy: string, sortOrder: string) => void;
  onSearch?: (search: string) => void;
  actions?: (item: T) => React.ReactNode;
}

export function DataTable<T extends { id: string }>({
  columns,
  data,
  total,
  skip,
  limit,
  hasMore,
  isLoading,
  onPageChange,
  onSortChange,
  onSearch,
  actions,
}: DataTableProps<T>) {
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const handleSearch = (value: string) => {
    setSearch(value);
    onSearch?.(value);
  };

  const handleSort = (key: string) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(key);
      setSortOrder('asc');
    }
    onSortChange?.(key, sortOrder === 'asc' ? 'desc' : 'asc');
  };

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="w-full space-y-4">
      {/* Search Bar */}
      {onSearch && (
        <div className="flex items-center gap-4">
          <input
            type="text"
            placeholder="Search..."
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className="px-6 py-3 text-left text-sm font-medium text-gray-700"
                  style={{ width: column.width }}
                >
                  {column.sortable && onSortChange ? (
                    <button
                      onClick={() => handleSort(String(column.key))}
                      className="flex items-center gap-2 hover:text-blue-600 transition"
                    >
                      {column.label}
                      {sortBy === String(column.key) && (
                        <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
              {actions && <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={columns.length + (actions ? 1 : 0)} className="px-6 py-4 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                    Loading...
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (actions ? 1 : 0)}
                  className="px-6 py-4 text-center text-gray-500"
                >
                  No data found
                </td>
              </tr>
            ) : (
              data.map((item) => (
                <tr key={item.id} className="border-t border-gray-200 hover:bg-gray-50 transition">
                  {columns.map((column) => (
                    <td key={String(column.key)} className="px-6 py-4 text-sm text-gray-900">
                      {column.render ? (
                        column.render(item)
                      ) : (
                        String(item[column.key] || '—')
                      )}
                    </td>
                  ))}
                  {actions && (
                    <td className="px-6 py-4 text-sm">
                      <div className="flex items-center gap-2">{actions(item)}</div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing <span className="font-medium">{skip + 1}</span> to{' '}
          <span className="font-medium">{Math.min(skip + limit, total)}</span> of{' '}
          <span className="font-medium">{total}</span> results
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(Math.max(0, skip - limit))}
            disabled={skip === 0}
            className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Previous
          </button>
          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
              const page = Math.max(1, Math.min(currentPage - 2, totalPages - 4)) + i;
              return (
                <button
                  key={page}
                  onClick={() => onPageChange((page - 1) * limit)}
                  className={`px-3 py-2 text-sm font-medium rounded-lg transition ${
                    currentPage === page
                      ? 'bg-blue-600 text-white'
                      : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {page}
                </button>
              );
            })}
          </div>
          <button
            onClick={() => onPageChange(skip + limit)}
            disabled={!hasMore}
            className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
