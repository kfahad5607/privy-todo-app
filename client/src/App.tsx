import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useEffect } from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginForm } from './features/auth/components/LoginForm';
import { RegisterForm } from './features/auth/components/RegisterForm';
import Todos from './features/todos/components/Todos';
import { useRefreshToken } from './hooks/useAuth';
import Home from './pages/Home';
import { UnauthenticatedRoute } from './components/UnauthenticatedRoute';

const queryClient = new QueryClient();

const App = () => {
  const refreshTokenMutation = useRefreshToken();

  useEffect(() => {
    refreshTokenMutation.mutate(undefined, {
      onSuccess: () => {
        console.log("Refresh token successful");
      }
    });

    return () => {
      console.log("Unmounting App");
      refreshTokenMutation.cancel();
    };
  }, []);

  if (refreshTokenMutation.isPending) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route element={<UnauthenticatedRoute />} >
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
        </Route>
        <Route element={<ProtectedRoute />} >
          <Route path="/todos" element={<Todos />} />
        </Route>
      </Routes>
    </Router>
  );
};

const AppWrapper = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export default AppWrapper;
