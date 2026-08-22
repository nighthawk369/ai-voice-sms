/**
 * Reusable UI components
 */

'use client';

import React from 'react';

// Loading Spinner
export function LoadingSpinner({
  size = 'md',
  text = 'Loading...',
}: {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex items-center justify-center gap-3">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-gray-300 border-t-blue-600`}
      />
      {text && <span className="text-gray-600">{text}</span>}
    </div>
  );
}

// Alert Component
export function Alert({
  type = 'info',
  title,
  message,
  onClose,
  action,
}: {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  onClose?: () => void;
  action?: { label: string; onClick: () => void };
}) {
  const bgColor = {
    info: 'bg-blue-50',
    success: 'bg-green-50',
    warning: 'bg-yellow-50',
    error: 'bg-red-50',
  };

  const borderColor = {
    info: 'border-blue-200',
    success: 'border-green-200',
    warning: 'border-yellow-200',
    error: 'border-red-200',
  };

  const textColor = {
    info: 'text-blue-800',
    success: 'text-green-800',
    warning: 'text-yellow-800',
    error: 'text-red-800',
  };

  return (
    <div className={`${bgColor[type]} ${borderColor[type]} border rounded-lg p-4 flex items-start justify-between`}>
      <div className="flex-1">
        {title && <h3 className={`font-medium ${textColor[type]}`}>{title}</h3>}
        <p className={`text-sm ${textColor[type]} mt-1`}>{message}</p>
      </div>
      <div className="flex items-center gap-2 ml-4">
        {action && (
          <button
            onClick={action.onClick}
            className={`px-3 py-1 text-sm font-medium rounded-lg ${
              type === 'error'
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : type === 'warning'
                  ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                  : type === 'success'
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            {action.label}
          </button>
        )}
        {onClose && (
          <button
            onClick={onClose}
            className={`text-sm font-medium ${textColor[type]} hover:opacity-75`}
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

// Button Component
export function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  children,
  className = '',
  type = 'button',
}: {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}) {
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-400',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 disabled:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-400',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50',
  };

  const sizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${variantClasses[variant]} ${sizeClasses[size]} rounded-lg font-medium transition disabled:cursor-not-allowed ${className}`}
    >
      {loading ? <LoadingSpinner size="sm" text="" /> : children}
    </button>
  );
}

// Input Component
export function Input({
  label,
  error,
  required = false,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
  required?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500"> *</span>}
        </label>
      )}
      <input
        {...props}
        className={`px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}

// Select Component
export function Select({
  label,
  error,
  options,
  required = false,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
  required?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500"> *</span>}
        </label>
      )}
      <select
        {...props}
        className={`px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      >
        <option value="">Select an option</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}

// Textarea Component
export function Textarea({
  label,
  error,
  required = false,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  error?: string;
  required?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500"> *</span>}
        </label>
      )}
      <textarea
        {...props}
        className={`px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      />
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}

// Card Component
export function Card({
  title,
  subtitle,
  children,
  actions,
}: {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
          <div>
            {title && <h2 className="text-lg font-semibold text-gray-900">{title}</h2>}
            {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="px-6 py-4">{children}</div>
    </div>
  );
}

// Badge Component
export function Badge({
  variant = 'gray',
  children,
}: {
  variant?: 'gray' | 'blue' | 'green' | 'yellow' | 'red';
  children: React.ReactNode;
}) {
  const variantClasses = {
    gray: 'bg-gray-100 text-gray-800',
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    red: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`${variantClasses[variant]} text-xs font-medium px-2 py-1 rounded-full`}>
      {children}
    </span>
  );
}

// Modal Component
export function Modal({
  isOpen,
  title,
  children,
  onClose,
  actions,
}: {
  isOpen: boolean;
  title?: string;
  children: React.ReactNode;
  onClose: () => void;
  actions?: React.ReactNode;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-md">
        {title && (
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
            >
              ×
            </button>
          </div>
        )}
        <div className="px-6 py-4">{children}</div>
        {actions && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-end gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

// Stats Card Component
export function StatsCard({
  label,
  value,
  change,
  icon,
}: {
  label: string;
  value: string | number;
  change?: { value: number; isPositive: boolean };
  icon?: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {change && (
            <p className={`text-sm mt-2 ${change.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {change.isPositive ? '↑' : '↓'} {Math.abs(change.value)}%
            </p>
          )}
        </div>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}
