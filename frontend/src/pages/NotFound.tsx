import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center text-text-primary font-sans">
      <div className="text-center">
        <AlertTriangle size={48} className="mx-auto mb-4 text-accent-yellow" />
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <p className="text-text-secondary mb-6">This page doesn't exist.</p>
        <Link to="/dashboard" className="btn-primary inline-flex">Back to Dashboard</Link>
      </div>
    </div>
  );
}
