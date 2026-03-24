import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth, UserRole } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRole?: UserRole;
}

export const ProtectedRoute = ({ children, allowedRole }: ProtectedRouteProps) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Wait for AuthContext to finish reading from localStorage before deciding
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If a specific role is required, check if user has that role
  if (allowedRole && user?.role !== allowedRole) {
    if (user?.role === 'student') {
      return <Navigate to="/student-dashboard" replace />;
    } else if (user?.role === 'teacher') {
      return <Navigate to="/teacher-dashboard" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};
