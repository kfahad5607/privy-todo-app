import { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth, useLogout } from '@/hooks/useAuth';

// Get user initials from full name
const getInitials = (name: string) => {
    return name
        .split(' ')
        .map(part => part[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
};

export function Layout() {
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const { authState, isAuthenticated } = useAuth();
    const logoutMutation = useLogout();
    const navigate = useNavigate();

    const user = authState?.user;

    const handleLogout = () => {
        logoutMutation.mutate(undefined, {
            onSuccess: () => {
                console.log('Logout successful');
                navigate('/login');
            }
        });
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navbar */}
            <nav className="bg-white shadow-sm">
                <div className="container mx-auto px-4">
                    <div className="flex justify-between items-center h-16">
                        {/* Left side - Logo and Nav Links */}
                        <div className="flex items-center space-x-8">
                            <Link to="/" className="text-xl font-bold text-gray-800">
                                Todo App
                            </Link>
                            <Link
                                to="/todos"
                                className="text-gray-600 hover:text-gray-900"
                            >
                                Todos
                            </Link>
                        </div>

                        {/* Right side - Profile Dropdown */}
                        {isAuthenticated && (
                            <div className="relative">
                                <button
                                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                                    className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 focus:outline-none"
                                >
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                                        <span className="text-sm font-medium text-blue-700">
                                            {user?.name ? getInitials(user.name) : 'U'}
                                        </span>
                                    </div>
                                    <span className="text-sm">{user?.username || 'Profile'}</span>
                                </button>

                                {/* Dropdown Menu */}
                                {isProfileOpen && (
                                    <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg py-1 z-10">
                                        {/* User Info Section */}
                                        <div className="px-4 py-2 border-b border-gray-100">
                                            <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                                            <p className="text-sm text-gray-500">{user?.email}</p>
                                        </div>

                                        {/* Actions Section */}
                                        <div className="py-1">
                                            <button
                                                onClick={handleLogout}
                                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                            >
                                                Logout
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>)
                        }
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                <Outlet />
            </main>
        </div>
    );
} 