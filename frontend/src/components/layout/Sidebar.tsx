'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Bus, 
  LayoutDashboard, 
  Users, 
  FileText, 
  Settings, 
  Activity 
} from 'lucide-react';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    name: 'Buses',
    href: '/buses',
    icon: Bus,
  },
  {
    name: 'Conductores',
    href: '/conductores',
    icon: Users,
    disabled: true,
  },
  {
    name: 'Reportes',
    href: '/reportes',
    icon: FileText,
    disabled: true,
  },
  {
    name: 'Sistema',
    href: '/sistema',
    icon: Activity,
  },
  {
    name: 'Configuración',
    href: '/configuracion',
    icon: Settings,
    disabled: true,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-white shadow-sm">
      {/* Logo */}
      <div className="flex h-16 items-center px-6 border-b border-gray-200">
        <Bus className="h-8 w-8 text-blue-600" />
        <span className="ml-2 text-xl font-semibold text-gray-900">
          Gestión de Flota
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.disabled ? '#' : item.href}
              className={cn(
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out',
                isActive
                  ? 'bg-blue-100 text-blue-700'
                  : item.disabled
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              )}
              onClick={(e) => {
                if (item.disabled) {
                  e.preventDefault();
                }
              }}
            >
              <Icon
                className={cn(
                  'mr-3 h-5 w-5 flex-shrink-0',
                  isActive
                    ? 'text-blue-700'
                    : item.disabled
                    ? 'text-gray-400'
                    : 'text-gray-500'
                )}
              />
              {item.name}
              {item.disabled && (
                <span className="ml-auto text-xs bg-gray-200 px-2 py-1 rounded">
                  Próximo
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p>Sistema de Gestión de Flota</p>
          <p>Versión 1.0.0</p>
        </div>
      </div>
    </div>
  );
}