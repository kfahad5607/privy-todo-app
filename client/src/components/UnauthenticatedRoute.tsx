import { Navigate, Outlet, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const UnauthenticatedRoute = () => {
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to={`/?${searchParams.toString()}`} replace />;
  }

  return <Outlet />;
};
