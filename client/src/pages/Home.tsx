import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Home = () => {
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to="/todos" replace />;
    }

    return <Navigate to="/login" replace />;
}

export default Home