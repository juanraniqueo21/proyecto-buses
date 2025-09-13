'use client';

import { useEffect, useState } from 'react';
import { Bus, Activity, AlertTriangle, TrendingUp } from 'lucide-react';
import { busesApi } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

interface DashboardStats {
  total_buses: number;
  total_eliminados: number;
  estados: Record<string, number>;  // ✅ CAMBIO: por_estado → estados
  capacidad_total_flota: number;
  kilometraje_promedio: number;     // ✅ AGREGADO: campo que devuelve la API
  fecha_consulta: string;
}

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  description?: string;
}

function StatsCard({ title, value, icon: Icon, color, description }: StatsCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 ${color}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('🔄 Fetching stats...');
        const data = await busesApi.getEstadisticas();
        console.log('✅ Stats received:', data);
        setStats(data);
      } catch (err) {
        console.error('❌ Error fetching stats:', err);
        setError('Error al cargar las estadísticas. Verifique que el backend esté funcionando.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="ml-4 text-gray-600">Cargando estadísticas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <AlertTriangle className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
              <p className="mt-1">Backend: http://localhost:8000</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center text-gray-500">
        No hay datos disponibles
      </div>
    );
  }

  // ✅ CAMBIO: Usar stats.estados en lugar de stats.por_estado
  const activeBuses = stats.total_buses;
  const totalBuses = activeBuses + stats.total_eliminados;
  const busesOperativos = stats.estados['Activo'] || 0;
  const busesMantenimiento = stats.estados['Mantenimiento'] || 0;
  const busesFueraServicio = stats.estados['Fuera de Servicio'] || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Vista general del sistema de gestión de flota
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total de Buses"
          value={formatNumber(totalBuses)}
          icon={Bus}
          color="text-blue-600"
          description={`${activeBuses} activos`}
        />
        
        <StatsCard
          title="Buses Operativos"
          value={formatNumber(busesOperativos)}
          icon={Activity}
          color="text-green-600"
          description="En servicio activo"
        />

        <StatsCard
          title="En Mantenimiento"
          value={formatNumber(busesMantenimiento)}
          icon={AlertTriangle}
          color="text-yellow-600"
          description="Requieren atención"
        />

        <StatsCard
          title="Capacidad Total"
          value={formatNumber(stats.capacidad_total_flota)}
          icon={TrendingUp}
          color="text-purple-600"
          description="Pasajeros sentados"
        />
      </div>

      {/* Estadísticas Adicionales */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Estado de la Flota */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Estado de la Flota</h2>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {Object.entries(stats.estados).map(([estado, cantidad]) => (
                <div key={estado} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      estado === 'Activo' ? 'bg-green-500' :
                      estado === 'Mantenimiento' ? 'bg-yellow-500' :
                      estado === 'Fuera de Servicio' ? 'bg-red-500' :
                      estado === 'Retirado' ? 'bg-gray-500' :
                      'bg-blue-500'
                    }`}></div>
                    <span className="text-sm font-medium text-gray-900">{estado}</span>
                  </div>
                  <span className="text-sm text-gray-600">{formatNumber(cantidad)} buses</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Métricas Adicionales */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Métricas de Flota</h2>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-900">Kilometraje Promedio</span>
              <span className="text-sm text-gray-600">{formatNumber(stats.kilometraje_promedio)} km</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-900">Buses Eliminados</span>
              <span className="text-sm text-gray-600">{formatNumber(stats.total_eliminados)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-900">Fuera de Servicio</span>
              <span className="text-sm text-gray-600">{formatNumber(busesFueraServicio)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Acciones Rápidas */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Acciones Rápidas</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <a
              href="/buses"
              className="block p-4 bg-blue-50 rounded-lg border border-blue-200 hover:bg-blue-100 transition-colors"
            >
              <Bus className="h-6 w-6 text-blue-600 mb-2" />
              <h3 className="font-medium text-blue-900">Gestionar Buses</h3>
              <p className="text-sm text-blue-700">Ver, crear y editar buses</p>
            </a>

            <a
              href="/buses/new"
              className="block p-4 bg-green-50 rounded-lg border border-green-200 hover:bg-green-100 transition-colors"
            >
              <TrendingUp className="h-6 w-6 text-green-600 mb-2" />
              <h3 className="font-medium text-green-900">Agregar Bus</h3>
              <p className="text-sm text-green-700">Registrar nuevo vehículo</p>
            </a>

            <a
              href="/sistema"
              className="block p-4 bg-purple-50 rounded-lg border border-purple-200 hover:bg-purple-100 transition-colors"
            >
              <Activity className="h-6 w-6 text-purple-600 mb-2" />
              <h3 className="font-medium text-purple-900">Estado Sistema</h3>
              <p className="text-sm text-purple-700">Verificar salud del sistema</p>
            </a>
          </div>
        </div>
      </div>

      {/* Footer con fecha */}
      <div className="text-center text-sm text-gray-500">
        Última actualización: {stats.fecha_consulta}
      </div>
    </div>
  );
}