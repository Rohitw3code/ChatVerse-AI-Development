import React from 'react';
import { Shield, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TermsAndConditionsPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden" style={{backgroundColor: '#0a0a0a'}}>
      <div className="absolute inset-0" style={{
        backgroundColor: '#0a0a0a',
        backgroundImage: `
          radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
          radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
          radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
        `,
        backgroundSize: '20px 20px, 40px 40px, 60px 60px'
      }}></div>
      <div className="absolute inset-0 opacity-20" style={{
        backgroundImage: `
          repeating-linear-gradient(
            90deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.03) 2px,
            rgba(255,255,255,0.03) 4px
          ),
          repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255,255,255,0.03) 2px,
            rgba(255,255,255,0.03) 4px
          )
        `
      }}></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/20"></div>

      <div className="relative z-10 max-w-4xl mx-auto px-6 py-20">
        <div className="mb-10">
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Home</span>
          </button>
        </div>
        <div className="text-center mb-12">
          <div className="inline-flex items-center space-x-3 bg-white/5 backdrop-blur-sm rounded-full px-6 py-3 border border-white/10 group animate-fade-in-down">
            <Shield className="w-5 h-5 text-green-300" />
            <span className="text-sm font-medium bg-gradient-to-r from-gray-300 to-white bg-clip-text text-transparent">TERMS & CONDITIONS</span>
          </div>
          <h1 className="text-5xl font-black mt-6 tracking-wide bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>
            Our Service Agreement
          </h1>
        </div>

        <div className="space-y-8 text-gray-300 leading-relaxed" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>
          <p>
            Welcome to ChatVerse. By accessing or using our service, you agree to be bound by the following terms and conditions.
          </p>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">1. Use of Service</h2>
            <p>
              ChatVerse is a social media automation tool. You agree to use our service in compliance with all applicable laws and regulations, and in a manner that does not infringe on the rights of others.
            </p>
            <p className="mt-2">
              You are responsible for all content posted and all activities that occur under your account. You agree not to use our service for any illegal or unauthorized purpose.
            </p>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">2. Account Responsibility</h2>
            <p>
              You are responsible for safeguarding the password that you use to access the service and for any activities or actions under your password. You agree not to disclose your password to any third party.
            </p>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">3. Intellectual Property</h2>
            <p>
              All intellectual property rights in the service, including the website, software, and content, are owned by ChatVerse or our licensors. Your use of the service does not grant you any ownership of any intellectual property rights in our service.
            </p>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">4. Termination</h2>
            <p>
              We may terminate or suspend your account immediately, without prior notice or liability, for any reason, including without limitation if you breach these terms.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsAndConditionsPage;