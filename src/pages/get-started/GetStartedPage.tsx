import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles, Zap, Rocket, Mail, Lock, LogIn, UserPlus } from 'lucide-react';
import { useAuthStore } from '../../stores';
import GoogleLoginButton from './components/GoogleLoginButton';
import { supabase } from '../../lib/supabase';
import { API_CONFIG } from '../../config/api'; // Import your API configuration
import FabricButton from '../landing/components/FabricButton';

const GetStartedPage: React.FC = () => {
  const { user, isLoading, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const [authMode, setAuthMode] = useState<'signIn' | 'signUp'>('signIn');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isEmailLoading, setIsEmailLoading] = useState(false);

  // No custom CSS injection; we use the landing page background/theme

  useEffect(() => {
    if (isAuthenticated && user) {
      navigate('/platforms');
    }
  }, [isAuthenticated, user, navigate]);

  const handleAuthAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (authMode === 'signUp' && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsEmailLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      let response;
      if (authMode === 'signIn') {
        response = await supabase.auth.signInWithPassword({ email, password });
      } else {
        response = await supabase.auth.signUp({ email, password });
      }
      
      const { error: authError, data } = response;

      if (authError) {
        setError(authError.message);
      } else if (data.user) {
        if (authMode === 'signUp') {
          // After successful Supabase sign-up, create profile in our backend
          const profilePayload = {
            provider_id: data.user.id,
            email: data.user.email,
            auth_provider: 'custom',
          };

          const profileResponse = await fetch(`${API_CONFIG.BASE_URL}/users/profile/custom`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profilePayload),
          });

          if (!profileResponse.ok) {
            const profileError = await profileResponse.json();
            setError(profileError.detail || 'Failed to create user profile.');
          } else {
            setSuccessMessage("Success! Please check your email to confirm your account.");
          }
        } else {
          // For sign-in, just navigate
          navigate('/platforms');
        }
      }
    } catch (err) {
      setError('An unexpected error occurred.');
    } finally {
      setIsEmailLoading(false);
    }
  };

  const toggleAuthMode = () => {
    setAuthMode(prev => prev === 'signIn' ? 'signUp' : 'signIn');
    setError(null);
    setSuccessMessage(null);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] text-white relative overflow-hidden flex items-center justify-center">
        <div className="fixed inset-0 bg-gradient-to-br from-[#0a0a0a] via-[#0f0f14] to-[#0a0a0a]" />
        <div
          className="fixed inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)`,
            backgroundSize: '64px 64px',
          }}
        />
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-orange-900/10 via-transparent to-transparent" />
        <div
          className="fixed inset-0 opacity-[0.015] mix-blend-overlay pointer-events-none"
          style={{
            backgroundImage:
              "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")",
          }}
        />
        <div className="relative z-10">
          <div className="w-8 h-8 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return null;
  }

  const FeatureCards = () => (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 lg:gap-4">
        <div className="group flex items-center gap-2 lg:gap-3 p-3 lg:p-4 rounded-lg lg:rounded-xl transition-all duration-300 bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 hover:border-white/20">
        <div className="p-1.5 lg:p-2 bg-gradient-to-br from-violet-500 to-purple-600 rounded-md lg:rounded-lg group-hover:scale-110 transition-transform duration-300">
            <Zap className="w-4 h-4 lg:w-5 lg:h-5 text-white" />
        </div>
        <div>
            <div className="text-xs lg:text-sm font-semibold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>Lightning Fast</div>
            <div className="text-[10px] lg:text-xs text-gray-400" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>Setup in 2 minutes</div>
        </div>
        </div>
        <div className="group flex items-center gap-2 lg:gap-3 p-3 lg:p-4 rounded-lg lg:rounded-xl transition-all duration-300 bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 hover:border-white/20">
        <div className="p-1.5 lg:p-2 bg-gradient-to-br from-pink-500 to-rose-600 rounded-md lg:rounded-lg group-hover:scale-110 transition-transform duration-300">
            <Rocket className="w-4 h-4 lg:w-5 lg:h-5 text-white" />
        </div>
        <div>
            <div className="text-xs lg:text-sm font-semibold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>AI Powered</div>
            <div className="text-[10px] lg:text-xs text-gray-400" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>Smart automation</div>
        </div>
        </div>
        <div className="group flex items-center gap-2 lg:gap-3 p-3 lg:p-4 rounded-lg lg:rounded-xl transition-all duration-300 bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 hover:border-white/20">
        <div className="p-1.5 lg:p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-md lg:rounded-lg group-hover:scale-110 transition-transform duration-300">
            <Sparkles className="w-4 h-4 lg:w-5 lg:h-5 text-white" />
        </div>
        <div>
            <div className="text-xs lg:text-sm font-semibold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>Multi-Platform</div>
            <div className="text-[10px] lg:text-xs text-gray-400" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>All in one place</div>
        </div>
        </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white relative overflow-hidden">
      {/* Landing background layers */}
      <div className="fixed inset-0 bg-gradient-to-br from-[#0a0a0a] via-[#0f0f14] to-[#0a0a0a]" />
      <div
        className="fixed inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)`,
          backgroundSize: '64px 64px',
        }}
      />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-orange-900/10 via-transparent to-transparent" />
      <div
        className="fixed inset-0 opacity-[0.015] mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E\")",
        }}
      />
      {/* Floating accents (kept subtle) */}
      <div className="absolute top-1/4 left-4 sm:left-8 md:left-20 hidden lg:block animate-float">
          <div className="w-2 h-2 bg-purple-400/60 rounded-full shadow-lg shadow-purple-400/30"></div>
      </div>
      <div className="absolute top-1/3 right-4 sm:right-8 md:right-32 hidden lg:block animate-float">
        <div className="w-3 h-3 bg-pink-400/50 rounded-full shadow-lg shadow-pink-400/30"></div>
      </div>
      <div className="absolute bottom-1/4 left-1/4 hidden lg:block animate-float">
        <div className="w-1 h-1 bg-white/40 rounded-full shadow-sm shadow-white/20"></div>
      </div>
      <div className="absolute top-1/2 left-1/3 hidden lg:block animate-float" style={{animationDelay: '1s'}}>
        <div className="w-1.5 h-1.5 bg-cyan-400/40 rounded-full shadow-sm shadow-cyan-400/20"></div>
      </div>
      <div className="absolute bottom-1/3 right-1/4 hidden lg:block animate-float" style={{animationDelay: '2s'}}>
        <div className="w-2.5 h-2.5 bg-violet-400/45 rounded-full shadow-md shadow-violet-400/25"></div>
      </div>

      <div className="absolute top-3 sm:top-4 left-3 sm:left-4 z-20">
        <Link
          to="/"
          className="group flex items-center gap-2 px-2 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-300"
        >
          <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5 text-gray-300 group-hover:text-white transition-colors duration-300" />
          <span className="font-medium text-gray-300 group-hover:text-white transition-colors duration-300 text-xs sm:text-sm" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>Back</span>
        </Link>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-3 sm:px-4 lg:px-6 py-8 sm:py-12">
        <div className="w-full max-w-6xl mx-auto">
          <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 items-center">
            
            <div className="lg:w-1/2 text-center lg:text-left space-y-4 lg:space-y-6">
                <div className="space-y-3 lg:space-y-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 lg:px-4 lg:py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-300">
                    <Sparkles className="w-4 h-4 lg:w-5 lg:h-5 text-purple-400 animate-pulse" />
                    <span className="text-xs lg:text-sm font-medium text-gray-300 tracking-wider" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>WELCOME ABOARD</span>
                    <div className="w-1.5 h-1.5 lg:w-2 lg:h-2 bg-white rounded-full animate-ping opacity-60"></div>
                    </div>

                    <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black leading-tight" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif', textShadow: '0 0 40px rgba(255,255,255,0.1)'}}>
                        <span className="text-white drop-shadow-lg">Welcome to</span>
                        <br />
                        <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-cyan-400 bg-clip-text text-transparent">
                            ChatVerse
                        </span>
                    </h1>
                </div>

                <p className="text-base lg:text-lg text-gray-400 max-w-lg mx-auto lg:mx-0 leading-relaxed" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>
                    Join thousands of creators who've revolutionized their social media presence with our AI-powered automation platform.
                </p>
                <div className="hidden lg:block pt-4 lg:pt-6">
                    <FeatureCards />
                </div>
            </div>

            <div className="w-full lg:w-1/2 flex justify-center lg:justify-end">
              <div className="w-full max-w-sm lg:max-w-md">
                <div className="relative p-6 lg:p-8 rounded-2xl lg:rounded-3xl bg-black/70 backdrop-blur-sm border border-gray-800 shadow-2xl shadow-purple-500/10">
                  <div className="absolute top-0 left-0 w-6 h-6 lg:w-8 lg:h-8 border-l-2 border-t-2 border-purple-400/40 rounded-tl-2xl lg:rounded-tl-3xl"></div>
                  <div className="absolute top-0 right-0 w-6 h-6 lg:w-8 lg:h-8 border-r-2 border-t-2 border-pink-400/40 rounded-tr-2xl lg:rounded-tr-3xl"></div>
                  <div className="absolute bottom-0 left-0 w-6 h-6 lg:w-8 lg:h-8 border-l-2 border-b-2 border-pink-400/40 rounded-bl-2xl lg:rounded-bl-3xl"></div>
                  <div className="absolute bottom-0 right-0 w-6 h-6 lg:w-8 lg:h-8 border-r-2 border-b-2 border-purple-400/40 rounded-br-2xl lg:rounded-br-3xl"></div>

                  <div className="relative z-10 text-center space-y-4 lg:space-y-6">
                    <div className="space-y-1 lg:space-y-2">
                      <h2 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>
                        {authMode === 'signIn' ? 'Welcome Back' : 'Create Account'}
                      </h2>
                      <p className="text-sm lg:text-base text-gray-400" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>
                        {authMode === 'signIn' ? 'Sign in to continue' : 'Join us to get started'}
                      </p>
                    </div>

                    <form onSubmit={handleAuthAction} className="space-y-4 text-left">
                       <div className="relative">
                           <Mail className="absolute top-1/2 -translate-y-1/2 left-3.5 w-5 h-5 text-gray-400" />
                           <input type="email" placeholder="Email Address" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full pl-11 pr-4 py-3 bg-black/70 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-600 transition-all duration-300" />
                       </div>
                       <div className="relative">
                           <Lock className="absolute top-1/2 -translate-y-1/2 left-3.5 w-5 h-5 text-gray-400" />
                           <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full pl-11 pr-4 py-3 bg-black/70 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-600 transition-all duration-300" />
                       </div>
                       
                       {authMode === 'signUp' && (
                           <div className="relative">
                               <Lock className="absolute top-1/2 -translate-y-1/2 left-3.5 w-5 h-5 text-gray-400" />
                               <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required className="w-full pl-11 pr-4 py-3 bg-black/70 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gray-600 transition-all duration-300" />
                           </div>
                       )}
                       
                       {error && <p className="text-red-400 text-sm text-center">{error}</p>}
                       {successMessage && <p className="text-green-400 text-sm text-center">{successMessage}</p>}
                       
                       <FabricButton type="submit" size="small" className="w-full rounded-lg text-sm py-3 px-4 sm:px-6" disabled={isEmailLoading}>
                         {isEmailLoading ? (
                           <div className="w-6 h-6 border-2 border-white/50 border-t-white rounded-full animate-spin"></div>
                         ) : (
                           <>
                             {authMode === 'signIn' ? <LogIn className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
                             <span>{authMode === 'signIn' ? 'Sign In' : 'Sign Up'}</span>
                           </>
                         )}
                       </FabricButton>
                    </form>
                    
                    <p className="text-sm text-gray-400">
                        {authMode === 'signIn' ? "Don't have an account?" : "Already have an account?"}{' '}
                        <button onClick={toggleAuthMode} className="font-semibold text-purple-400 hover:text-purple-300 transition-colors">
                            {authMode === 'signIn' ? 'Sign Up' : 'Sign In'}
                        </button>
                    </p>

                    <div className="flex items-center gap-4">
                        <hr className="w-full border-white/10" />
                        <span className="text-gray-500 text-xs font-semibold">OR</span>
                        <hr className="w-full border-white/10" />
                    </div>

                    <div>
                      <GoogleLoginButton />
                    </div>
                  </div>

                  <div className="pt-6 border-t border-white/10 mt-6">
                    <p className="text-xs text-gray-500 leading-relaxed text-center px-2" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>
                      By continuing, you agree to our{' '}
                      <a href="/terms" className="text-purple-400 hover:text-purple-300 transition-colors">
                        Terms of Service
                      </a>{' '}
                      &{' '}
                      <a href="/privacy" className="text-purple-400 hover:text-purple-300 transition-colors">
                        Privacy Policy
                      </a>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="lg:hidden w-full max-w-md pt-12 mt-8 border-t border-white/10">
                <FeatureCards />
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default GetStartedPage;

