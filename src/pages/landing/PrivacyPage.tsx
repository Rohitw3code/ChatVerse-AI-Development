import React from 'react';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PrivacyPage = () => {
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
            <Sparkles className="w-5 h-5 text-purple-300" />
            <span className="text-sm font-medium bg-gradient-to-r from-gray-300 to-white bg-clip-text text-transparent">PRIVACY POLICY</span>
          </div>
          <h1 className="text-5xl font-black mt-6 tracking-wide bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, Inter, system-ui, sans-serif'}}>
            Your Privacy Matter
          </h1>
        </div>

        <div className="space-y-8 text-gray-300 leading-relaxed" style={{fontFamily: 'Inter, system-ui, sans-serif'}}>
          <p>
            At ChatVerse, we are committed to protecting your privacy while providing powerful Instagram automation features. This policy outlines how we collect, use, and protect your information when using our Instagram Comment API, messaging automation, and AI-driven engagement tools.
          </p>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">1. Information We Collect</h2>
            <p>
              We collect information that you provide directly to us, such as when you create an account or connect your Instagram profile. This may include your name, email address, and authentication tokens for Instagram.
            </p>
            <p className="mt-2">
              <strong className="text-white">Instagram-Specific Data Collection:</strong>
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Instagram post IDs and content for comment automation targeting</li>
              <li>Comment data from your Instagram posts for keyword detection and AI analysis</li>
              <li>Instagram direct messages for messaging automation features</li>
              <li>User engagement metrics and interaction patterns</li>
              <li>Automation settings including comment reply counts and trigger keywords</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">2. Instagram Comment API Usage</h2>
            <p>
              Our Instagram Comment API integration enables automated comment replies on your posts. Here's how we handle your data:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li><strong className="text-white">Post Selection:</strong> You can choose specific post IDs or enable automation for ALL posts</li>
              <li><strong className="text-white">Keyword Detection:</strong> We analyze comments for specified keywords to trigger automated responses</li>
              <li><strong className="text-white">AI Decision Making:</strong> Our AI evaluates comment context to determine appropriate responses</li>
              <li><strong className="text-white">Reply Limits:</strong> You control the maximum number of automated comment replies per post</li>
              <li><strong className="text-white">Data Retention:</strong> Comment data is processed in real-time and stored only for automation purposes</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">3. Instagram Messaging Automation</h2>
            <p>
              Our messaging features allow you to load Instagram messages into ChatVerse and create automated responses:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li><strong className="text-white">Message Loading:</strong> We securely access your Instagram direct messages with your explicit consent</li>
              <li><strong className="text-white">Quick Messages:</strong> Automated sending of pre-configured text, images, and button templates</li>
              <li><strong className="text-white">Context-Based Triggers:</strong> AI analyzes message content to determine when to send automated responses</li>
              <li><strong className="text-white">Template Messages:</strong> Support for plain text, rich media, and interactive button templates</li>
              <li><strong className="text-white">User Control:</strong> You maintain full control over when and how automated messages are sent</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">4. AI Automation and Decision Making</h2>
            <p>
              Our AI systems analyze your Instagram interactions to provide intelligent automation:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li><strong className="text-white">Context Analysis:</strong> AI evaluates message and comment context to make appropriate response decisions</li>
              <li><strong className="text-white">Keyword Matching:</strong> Advanced keyword detection algorithms identify relevant engagement opportunities</li>
              <li><strong className="text-white">Response Generation:</strong> AI creates contextually appropriate replies based on your brand voice and preferences</li>
              <li><strong className="text-white">Learning Patterns:</strong> The system learns from your engagement patterns to improve automation accuracy</li>
              <li><strong className="text-white">Human Oversight:</strong> You can review and modify AI decisions before they are executed</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">5. How We Use Your Instagram Data</h2>
            <p>
              We use your Instagram data exclusively to provide automation services:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>To enable automated comment replies based on your specified criteria</li>
              <li>To facilitate messaging automation and quick response features</li>
              <li>To train AI models for better context understanding and response generation</li>
              <li>To provide analytics and insights on your Instagram engagement</li>
              <li>To improve the accuracy and effectiveness of automation features</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">6. Instagram API Compliance</h2>
            <p>
              We strictly adhere to Instagram's API Terms of Service and privacy requirements:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>All Instagram data access requires explicit user authorization</li>
              <li>We only access data necessary for the specific automation features you enable</li>
              <li>Instagram data is not shared with unauthorized third parties</li>
              <li>We comply with Instagram's rate limits and usage guidelines</li>
              <li>Users can revoke Instagram access permissions at any time</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">7. Data Security and Protection</h2>
            <p>
              We implement robust security measures to protect your Instagram data:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>All Instagram API communications are encrypted using industry-standard protocols</li>
              <li>Authentication tokens are securely stored and regularly rotated</li>
              <li>Access to Instagram data is limited to authorized personnel and systems</li>
              <li>We maintain audit logs of all Instagram data access and usage</li>
              <li>Regular security assessments ensure ongoing protection of your data</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">8. User Control and Consent</h2>
            <p>
              You maintain full control over your Instagram automation settings:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Granular control over which posts and messages are automated</li>
              <li>Ability to set custom keywords and response triggers</li>
              <li>Option to review AI-generated responses before they are sent</li>
              <li>Easy disconnection of Instagram account from ChatVerse</li>
              <li>Deletion of all Instagram data upon account disconnection</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">9. Third-Party Sharing</h2>
            <p>
              We do not sell your Instagram data to third parties. Instagram data may only be shared with:
            </p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>Instagram/Meta platforms as required for API functionality</li>
              <li>Trusted service providers who assist in providing automation services</li>
              <li>Legal authorities when required by law or to protect our users</li>
            </ul>
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white mb-4">10. Contact Information</h2>
            <p>
              If you have questions about this privacy policy or our Instagram data practices, please contact us at:
            </p>
            <p className="mt-2">
              <strong className="text-white">Email:</strong> privacy@chatverse.io<br/>
              <strong className="text-white">Privacy Page:</strong> <a href="/privacy" className="text-cyan-400 hover:text-cyan-300 transition-colors">chatverse.io/privacy</a>
            </p>
          </div>

          <div className="bg-gradient-to-r from-purple-900/20 to-cyan-900/20 border border-purple-500/20 rounded-lg p-6 mt-8">
            <h3 className="text-xl font-bold text-white mb-3">Instagram Automation Features Summary</h3>
            <p className="text-sm text-gray-300">
              ChatVerse provides comprehensive Instagram automation including comment replies with keyword detection, 
              AI-powered decision making for engagement, customizable reply limits, direct message automation with 
              template support, and context-aware triggers. All features respect Instagram's API guidelines and 
              prioritize user privacy and control.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPage;