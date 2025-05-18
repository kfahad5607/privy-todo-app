import { Navigate, Outlet, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const ProtectedRoute = () => {
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to={`/login?${searchParams.toString()}`} replace />;
  }

  return <Outlet />;
};
