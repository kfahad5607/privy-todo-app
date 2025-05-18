import { Navigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Home = () => {
    const [searchParams] = useSearchParams();
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to={`/todos?${searchParams.toString()}`} replace />;
    }

    return <Navigate to={`/login?${searchParams.toString()}`} replace />;
}

export default Home