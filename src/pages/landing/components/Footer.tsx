import React from 'react';
import { Instagram, Facebook, Twitter, Linkedin } from 'lucide-react';
import chatverseLogo from '../../../components/chatverse1.svg';

const Footer: React.FC = () => {
  return (
    <footer className="relative z-10 border-t border-white/10 bg-black/50 backdrop-blur-lg mt-24">
      <div className="max-w-5xl mx-auto px-6 py-12 text-gray-400">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center border border-white/10">
                <img src={chatverseLogo} alt="ChatVerse Logo" className="w-full h-full" />
              </div>
              <span className="text-2xl font-bold text-white tracking-wide">ChatVerse.io</span>
            </div>
            <p className="text-sm">Intelligent social media automation to connect, automate, and engage across all platforms.</p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Blog
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/privacy" className="hover:text-white transition-colors duration-200" target="_blank">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="/terms" className="hover:text-white transition-colors duration-200" target="_blank">
                  Terms & Conditions
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors duration-200">
                  Disclaimer
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col md:flex-row items-center justify-between border-t border-white/10 pt-8">
          <div className="text-sm">&copy; {new Date().getFullYear()} ChatVerse. All rights reserved.</div>
          <div className="flex items-center space-x-4 mt-6 md:mt-0">
            <a href="#" className="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm flex items-center justify-center hover:scale-110 transition-all duration-300 border border-white/20 hover:border-white/40">
              <Instagram className="w-4 h-4 text-gray-400 hover:text-white" />
            </a>
            <a href="#" className="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm flex items-center justify-center hover:scale-110 transition-all duration-300 border border-white/20 hover:border-white/40">
              <Facebook className="w-4 h-4 text-gray-400 hover:text-white" />
            </a>
            <a href="#" className="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm flex items-center justify-center hover:scale-110 transition-all duration-300 border border-white/20 hover:border-white/40">
              <Twitter className="w-4 h-4 text-gray-400 hover:text-white" />
            </a>
            <a href="#" className="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm flex items-center justify-center hover:scale-110 transition-all duration-300 border border-white/20 hover:border-white/40">
              <Linkedin className="w-4 h-4 text-gray-400 hover:text-white" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
