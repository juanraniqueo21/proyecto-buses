'use client';

import { useEffect, useState } from 'react';
import { Bell, User, Activity } from 'lucide-react';
import { systemApi } from '@/lib/api';

interface SystemHealth {
  status: string;
  api: string;
  database: string;
}

export function Header() {
  const [healthStatus, setHealthStatus] = useState<SystemHealth | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await systemApi.getHealth();
        setHealthStatus(health);
      } catch (error) {
        console.error('Error checking health:', error);
        setHealthStatus({
          status: 'error',
          api: 'error',
          database: 'error'
        });
      }
    };

    checkHealth();
    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'operational':
        return 'text-green-600';
      case 'connected':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Page title area */}
        <div className="flex items-center">
          <h1 className="text-2xl font-semibold text-gray-900">
            Sistema de Gestión de Flota
          </h1>
        </div>

        {/* Right side - Status and user info */}
        <div className="flex items-center space-x-4">
          {/* System health status */}
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">Estado:</span>
            {healthStatus ? (
              <span className={`text-sm font-medium ${getStatusColor(healthStatus.status)}`}>
                {healthStatus.status === 'healthy' ? 'Saludable' : 
                 healthStatus.status === 'degraded' ? 'Degradado' : 'Error'}
              </span>
            ) : (
              <span className="text-sm text-gray-400">Verificando...</span>
            )}
          </div>

          {/* Notifications */}
          <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors">
            <Bell className="h-5 w-5" />
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-blue-600" />
              </div>
              <div className="text-sm">
                <p className="text-gray-900 font-medium">Administrador</p>
                <p className="text-gray-500">Sistema</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}