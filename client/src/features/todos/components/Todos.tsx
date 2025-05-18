import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useLogout } from '../../../hooks/useAuth';

const Todos = () => {
    const navigate = useNavigate();
    const logoutMutation = useLogout();
    const { authState } = useAuth();
    const handleLogout = () => {
        logoutMutation.mutate(undefined, {
            onSuccess: () => {
                navigate('/login');
            }
        });
    }
    
  return (
    <div>
        <h1>Todos</h1>
        <p>Hello {authState?.user?.name}</p>
        <button onClick={handleLogout}>Logout</button>
        <div>
        <Link to="/login">Login</Link>
        </div>
            
    </div>
  )
}

export default Todos