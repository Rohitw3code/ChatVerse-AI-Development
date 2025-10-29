import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useAuthStore } from '../../../stores';
import FabricButton from './FabricButton';
import chatverseLogo from '../../../components/chatverse1.svg';

interface NavigationProps {
  isMenuOpen: boolean;
  setIsMenuOpen: (open: boolean) => void;
}

const Navigation: React.FC<NavigationProps> = ({ isMenuOpen, setIsMenuOpen }) => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    const { signOut } = useAuthStore.getState();
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <nav className="relative z-50">
      <div className="max-w-5xl mx-auto px-6 py-2">
        <div className="flex items-center justify-between">
          <div className="hidden md:flex items-center space-x-3">
            <div className="relative group">
              <div className="w-8 h-8 backdrop-blur-sm flex items-center justify-center transition-all duration-300 hover:scale-105">
                <img src={chatverseLogo} alt="ChatVerse Logo" className="w-full h-full" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 opacity-80"></div>
            </div>
            <span className="text-2xl font-bold text-white tracking-wide">ChatVerse.io</span>
          </div>

          <div className="hidden md:flex items-center justify-end flex-1">
            <div className="flex items-center space-x-8">
              <a href="#platform" className="relative group">
                <span className="text-gray-400 hover:text-white transition-all duration-300">Platform</span>
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-500"></div>
              </a>
              <button onClick={() => navigate('/pricing')} className="relative group">
                <span className="text-gray-400 hover:text-white transition-all duration-300">Pricing</span>
                <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-white group-hover:w-full transition-all duration-500"></div>
              </button>
              <div className="flex items-center space-x-4">
                {user ? (
                  <>
                    <button 
                      onClick={() => navigate('/platforms')}
                      className="px-4 py-2 text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Dashboard
                    </button>
                    {/* Logout button removed from desktop */}
                  </>
                ) : (
                  <>
                    <button 
                      onClick={() => navigate('/get-started')}
                      className="px-4 py-2 text-gray-400 hover:text-white transition-all duration-300"
                    >
                      Login
                    </button>
                    <FabricButton 
                      onClick={() => navigate('/get-started')}
                      variant="secondary"
                      size="small"
                    >
                      Sign Up
                    </FabricButton>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="md:hidden flex-1 flex justify-end">
            <button className="transition-transform duration-200" onClick={() => setIsMenuOpen(!isMenuOpen)}>
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-black/90 backdrop-blur-lg border border-white/20 rounded-lg mt-2 mx-6 p-4">
            <div className="flex flex-col space-y-4">
              <a href="#platform" className="text-gray-400 hover:text-white transition-all duration-300">
                Platform
              </a>
              <button 
                onClick={() => navigate('/pricing')}
                className="text-left text-gray-400 hover:text-white transition-all duration-300"
              >
                Pricing
              </button>
              {user ? (
                <>
                  <button 
                    onClick={() => navigate('/platforms')}
                    className="text-left text-gray-400 hover:text-white transition-all duration-300"
                  >
                    Dashboard
                  </button>
                  <button 
                    onClick={handleLogout}
                    className="px-6 py-2 bg-red-500/10 backdrop-blur-sm rounded-lg text-center border border-red-500/20 hover:bg-red-500/20 transition-all duration-300"
                  >
                    <span className="text-red-400">Logout</span>
                  </button>
                </>
              ) : (
                <>
                  <button 
                    onClick={() => navigate('/get-started')}
                    className="text-left text-gray-400 hover:text-white transition-all duration-300"
                  >
                    Login
                  </button>
                  <FabricButton 
                    onClick={() => navigate('/get-started')}
                    variant="secondary"
                    size="small"
                  >
                    Sign Up
                  </FabricButton>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
