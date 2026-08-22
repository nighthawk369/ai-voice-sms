'use client';

import { useState, useEffect } from 'react';

interface BusinessType {
  value: string;
  label: string;
  category: string;
  description: string;
}

interface BusinessTypeSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function BusinessTypeSelector({
  value,
  onChange,
  disabled = false,
}: BusinessTypeSelectorProps) {
  const [businessTypes, setBusinessTypes] = useState<BusinessType[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinessTypes();
  }, []);

  const fetchBusinessTypes = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/business-types');
      const data = await response.json();
      setBusinessTypes(data.business_types);
      setCategories(data.categories);
    } catch (error) {
      console.error('Error fetching business types:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupedByCategory = businessTypes.reduce(
    (acc, bt) => {
      if (!acc[bt.category]) {
        acc[bt.category] = [];
      }
      acc[bt.category].push(bt);
      return acc;
    },
    {} as Record<string, BusinessType[]>
  );

  const selectedBT = businessTypes.find((bt) => bt.value === value);

  return (
    <div className="business-type-selector">
      <label htmlFor="business-type" className="label">
        Business Type
        <span className="text-red-500">*</span>
      </label>

      <select
        id="business-type"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled || loading}
        className="select select-bordered w-full"
      >
        <option value="">-- Select your business type --</option>

        {Object.entries(groupedByCategory).map(([category, types]) => (
          <optgroup
            key={category}
            label={category.charAt(0).toUpperCase() + category.slice(1)}
          >
            {types.map((bt) => (
              <option key={bt.value} value={bt.value}>
                {bt.label}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      {selectedBT && (
        <div className="mt-3 p-3 bg-blue-50 rounded border border-blue-200">
          <p className="text-sm font-medium text-blue-900">{selectedBT.label}</p>
          <p className="text-xs text-blue-700 mt-1">{selectedBT.description}</p>
        </div>
      )}

      <style jsx>{`
        .business-type-selector {
          width: 100%;
        }

        .label {
          display: block;
          font-weight: 500;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .select {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ccc;
          border-radius: 0.375rem;
          font-size: 0.875rem;
        }

        .select:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .select:disabled {
          background-color: #f3f4f6;
          color: #6b7280;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}
