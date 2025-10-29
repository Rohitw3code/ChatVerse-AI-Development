import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Check, Star, Zap, Crown, Rocket, ArrowRight, Sparkles } from 'lucide-react';
import { PlansApiService, BillingPlan } from '../../api/plans_api';
import { useUserStore } from '../../stores/userStore';
import { ENV } from '../../config/environment';

declare global {
  interface Window {
    Razorpay: any;
  }
}

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  period: string;
  description: string;
  features: string[];
  credits: number;
  popular?: boolean;
  premium?: boolean;
  icon: React.ElementType;
  gradient: string;
  buttonText: string;
}

const PricingPage: React.FC = () => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [backendPlans, setBackendPlans] = useState<BillingPlan[]>([]);
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [processingPlanId, setProcessingPlanId] = useState<string | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const userProfile = useUserStore((s) => s.userProfile);

  // Handle mouse movement for background effect
  const handleMouseMove = useCallback((e: MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  }, []);

  // Add mouse move listener
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  // Inject CSS for dynamic background effect and fabric styling
  useEffect(() => {
    const styleId = 'pricing-fabric-styles';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .mouse-pull-bg {
        transition: transform 0.3s ease-out, filter 0.3s ease-out;
        will-change: transform, filter;
      }
      
      .mouse-pull-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
          rgba(255,255,255,0.08) 0%, 
          rgba(255,255,255,0.04) 20%, 
          rgba(255,255,255,0.02) 40%, 
          transparent 60%);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease-out;
      }
      
      .mouse-pull-bg:hover::before {
        opacity: 1;
      }
      
      .pricing-card {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.015) 0px, rgba(255,255,255,0.015) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(30,30,30,0.6) 0%, rgba(20,20,20,0.4) 100%);
        background-size: 40px 40px, 40px 40px, 100% 100%;
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
      }
      
      .pricing-card:hover {
        background: 
          repeating-linear-gradient(45deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 20px),
          repeating-linear-gradient(-45deg, rgba(255,255,255,0.025) 0px, rgba(255,255,255,0.025) 1px, transparent 1px, transparent 20px),
          linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.6) 100%);
        background-size: 44px 44px, 44px 44px, 100% 100%;
        border-color: rgba(255, 255, 255, 0.25);
        transform: translateY(-4px) scale(1.02);
      }
      
      .pricing-card.popular:hover {
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 25px 50px -12px rgba(139, 92, 246, 0.25);
      }
      
      .pricing-card.premium:hover {
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 25px 50px -12px rgba(245, 158, 11, 0.25);
      }
      
      .fabric-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
          radial-gradient(circle at 25% 25%, rgba(255,255,255,0.015) 0%, transparent 50%),
          radial-gradient(circle at 75% 75%, rgba(255,255,255,0.01) 0%, transparent 50%);
        opacity: 0;
        transition: opacity 0.5s ease;
        pointer-events: none;
      }
      
      .pricing-card:hover .fabric-overlay {
        opacity: 1;
      }
      
      .fabric-btn {
        background: 
          radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.08) 0px,
            rgba(255, 255, 255, 0.08) 1px,
            transparent 1px,
            transparent 8px
          ),
          repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.04) 0px,
            rgba(255, 255, 255, 0.04) 1px,
            transparent 1px,
            transparent 12px
          ),
          linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #0a0a0a 100%);
        background-size: 200% 200%, 150% 150%, 16px 16px, 24px 24px, 100% 100%;
        background-blend-mode: overlay, multiply, normal, normal, normal;
        border: 2px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
      }
      
      .fabric-btn:hover {
        background-size: 220% 220%, 170% 170%, 18px 18px, 26px 26px, 100% 100%;
        border-color: rgba(255, 255, 255, 0.25);
        box-shadow: 
          0 0 30px rgba(255, 255, 255, 0.2),
          0 8px 32px rgba(0, 0, 0, 0.4),
          inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transform: translateY(-2px) scale(1.02);
      }
      
      .fabric-btn.popular {
        background: 
          radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.2) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(139, 92, 246, 0.1) 0px,
            rgba(139, 92, 246, 0.1) 1px,
            transparent 1px,
            transparent 8px
          ),
          linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%);
        border-color: rgba(139, 92, 246, 0.4);
      }
      
      .fabric-btn.popular:hover {
        box-shadow: 
          0 0 30px rgba(139, 92, 246, 0.4),
          0 8px 32px rgba(139, 92, 246, 0.3);
      }
      
      .fabric-btn.premium {
        background: 
          radial-gradient(circle at 20% 20%, rgba(245, 158, 11, 0.2) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(245, 158, 11, 0.1) 0%, transparent 50%),
          repeating-linear-gradient(
            45deg,
            rgba(245, 158, 11, 0.1) 0px,
            rgba(245, 158, 11, 0.1) 1px,
            transparent 1px,
            transparent 8px
          ),
          linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%);
        border-color: rgba(245, 158, 11, 0.4);
      }
      
      .fabric-btn.premium:hover {
        box-shadow: 
          0 0 30px rgba(245, 158, 11, 0.4),
          0 8px 32px rgba(245, 158, 11, 0.3);
      }
    `;
    document.head.appendChild(style);
  }, []);

  const loadRazorpayScript = (): Promise<boolean> => {
    return new Promise((resolve) => {
      if (typeof window !== 'undefined' && window.Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const iconForPlan = (name: string): React.ElementType => {
    const lower = name.toLowerCase();
    if (lower.includes('enterprise')) return Crown;
    if (lower.includes('pro')) return Star;
    if (lower.includes('starter') || lower.includes('basic')) return Zap;
    return Rocket;
  };

  const gradientForPlan = (name: string): string => {
    const lower = name.toLowerCase();
    if (lower.includes('enterprise')) return 'from-amber-500 to-orange-500';
    if (lower.includes('pro')) return 'from-purple-500 to-pink-500';
    return 'from-blue-500 to-cyan-500';
  };

  const mapToPricingPlan = (p: BillingPlan): PricingPlan => {
    const isYearly = billingCycle === 'yearly';
    const monthlyPrice = p.monthly_price;
    const yearlyPrice = p.yearly_price;
    const features = p.metadata?.features || [];
    
    let price: number;
    let originalPrice: number | undefined;
    let credits: number;

    if (isYearly) {
      price = yearlyPrice ?? +(monthlyPrice * 10).toFixed(2);
      originalPrice = +(monthlyPrice * 12).toFixed(2);
      credits = p.yearly_credits || p.monthly_credits * 12;
    } else {
      price = monthlyPrice;
      originalPrice = undefined;
      credits = p.monthly_credits;
    }
    
    const period = isYearly ? '/year' : '/month';

    return {
      id: String(p.id),
      name: p.name,
      price,
      originalPrice,
      period,
      description: `${p.name} subscription plan`,
      credits,
      features,
      popular: !!p.metadata?.popular,
      premium: p.name.toLowerCase().includes('enterprise'),
      icon: iconForPlan(p.name),
      gradient: gradientForPlan(p.name),
      buttonText: p.name.toLowerCase().includes('pro') ? 'Start Free Trial' : 'Choose Plan',
    };
  };

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        setLoading(true);
        const resp = await PlansApiService.getBillingPlans();
        if (isMounted) {
          setBackendPlans(resp.data || []);
        }
      } catch (e) {
        console.error('Failed to load billing plans', e);
      } finally {
        if (isMounted) setLoading(false);
      }
    })();
    return () => { isMounted = false; };
  }, []);

  useEffect(() => {
    const isYearly = billingCycle === 'yearly';

    const freePlan: PricingPlan = {
      id: 'free-plan',
      name: 'Free',
      price: 0,
      period: '/month',
      description: 'Perfect for getting started and exploring the platform.',
      credits: isYearly ? 100 * 365 : 100 * 30,
      features: [
        '100 credits per day',
        '1,000 Social Media Automations for Instagram',
        'Basic support',
      ],
      popular: false,
      premium: false,
      icon: Zap,
      gradient: 'from-gray-600 to-gray-700',
      buttonText: 'Choose Plan',
    };

    const uiPlans = backendPlans.map(mapToPricingPlan);
    setPlans([freePlan, ...uiPlans]);
  }, [backendPlans, billingCycle]);

  const handlePlanSelect = async (planId: string) => {
    if (processingPlanId || planId === 'free-plan') return;
    const selectedPlan = plans.find(p => p.id === planId);
    try {
      setProcessingPlanId(planId);
      if (!userProfile?.provider_id) {
        console.error('User not available in store.');
        alert('Please sign in to continue.');
        return;
      }

      const created = await PlansApiService.createOrder({
        plan_id: planId,
        user_id: userProfile.provider_id,
        billing_cycle: billingCycle,
      });

      if (!created?.success || !created?.data) {
        throw new Error(created?.message || 'Failed to create order');
      }

      const data = created.data;
      const success = await loadRazorpayScript();
      if (!success) {
        throw new Error('Failed to load Razorpay SDK');
      }

      const {
        razorpay_key_id: key,
        order_id: orderId,
        amount,
        currency,
      } = data;

      if (!key || !orderId) {
        throw new Error('Razorpay configuration missing (key/order_id)');
      }

      const rzp = new window.Razorpay({
        key,
        amount,
        currency,
        name: ENV.app.name || 'ChatVerse',
        description: `${selectedPlan?.name || 'Plan'} subscription (${billingCycle})`,
        order_id: orderId,
        prefill: {
          name: userProfile.full_name || '',
          email: userProfile.email || '',
        },
        theme: { color: '#6d28d9' },
        handler: async function (response: any) {
          try {
            const cb = await PlansApiService.paymentCallback({
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
              plan_id: planId,
              user_id: userProfile.provider_id,
            });
            if (!cb.success) {
              throw new Error(cb.message || 'Payment verification failed');
            }
            alert('Payment successful! Your plan will be activated shortly.');
          } catch (err: any) {
            console.error(err);
            alert(err?.message || 'Payment verification failed');
          } finally {
            setProcessingPlanId(null);
          }
        },
      });

      rzp.on('payment.failed', (resp: any) => {
        console.error('Payment failed:', resp?.error);
        alert(resp?.error?.description || 'Payment failed');
        setProcessingPlanId(null);
      });

      rzp.open();
    } catch (error: any) {
      console.error('Failed to initiate payment:', error);
      alert(error?.message || 'Failed to initiate payment');
      setProcessingPlanId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen text-white relative overflow-hidden flex items-center justify-center" style={{ backgroundColor: '#0a0a0a' }}>
        <div className="w-10 h-10 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden" style={{ backgroundColor: '#0a0a0a' }}>
      {/* Multi-layer Background with Mouse Pull Effect */}
      <div
        className="absolute inset-0 mouse-pull-bg"
        style={{
          backgroundColor: '#0a0a0a',
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0),
            radial-gradient(circle at 3px 3px, rgba(255,255,255,0.08) 1px, transparent 0),
            radial-gradient(circle at 5px 5px, rgba(255,255,255,0.04) 1px, transparent 0)
          `,
          backgroundSize: '20px 20px, 40px 40px, 60px 60px',
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.02}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.02}px)`,
          '--mouse-x': `${typeof window !== 'undefined' ? (mousePosition.x / window.innerWidth) * 100 : 50}%`,
          '--mouse-y': `${typeof window !== 'undefined' ? (mousePosition.y / window.innerHeight) * 100 : 50}%`,
        } as React.CSSProperties}
      ></div>
      
      {/* Dynamic pull effect overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle 200px at ${mousePosition.x}px ${mousePosition.y}px, 
            rgba(255,255,255,0.03) 0%, 
            rgba(255,255,255,0.01) 50%, 
            transparent 70%)`,
          opacity: mousePosition.x > 0 ? 1 : 0,
          transition: 'opacity 0.3s ease-out',
        }}
      ></div>

      <div
        className="absolute inset-0 opacity-20"
        style={{
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
          `,
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.01}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.01}px)`,
          transition: 'transform 0.2s ease-out',
        }}
      ></div>

      <div 
        className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-gray-900/20"
        style={{
          transform: `translate(${(mousePosition.x - (typeof window !== 'undefined' ? window.innerWidth : 0) / 2) * 0.005}px, ${(mousePosition.y - (typeof window !== 'undefined' ? window.innerHeight : 0) / 2) * 0.005}px)`,
          transition: 'transform 0.4s ease-out',
        }}
      ></div>
      
      {/* Upward pull effect for dots near cursor */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle 150px at ${mousePosition.x}px ${mousePosition.y - 20}px, 
            rgba(255,255,255,0.1) 0%, 
            rgba(255,255,255,0.05) 30%, 
            transparent 60%)`,
          opacity: mousePosition.x > 0 ? 0.8 : 0,
          transition: 'opacity 0.2s ease-out',
          filter: 'blur(1px)',
        }}
      ></div>

      <div className="relative z-10 p-4 sm:p-6 lg:p-8 font-sans" style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
        <div className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b border-white/5" style={{ backgroundColor: '#0a0a0a' }}>
          {/* Matching Background Pattern */}
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: `
              radial-gradient(circle at 1px 1px, rgba(255,255,255,0.08) 1px, transparent 0),
              radial-gradient(circle at 3px 3px, rgba(255,255,255,0.04) 1px, transparent 0),
              radial-gradient(circle at 5px 5px, rgba(255,255,255,0.02) 1px, transparent 0)
            `,
            backgroundSize: '20px 20px, 40px 40px, 60px 60px'
          }}></div>
          {/* Subtle Fabric Overlay */}
          <div className="absolute inset-0 opacity-20" style={{
            backgroundImage: `
              repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px),
              repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px)
            `
          }}></div>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="flex justify-between items-center h-14 sm:h-16">
              <Link to="/platforms" className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-black/80 via-gray-900/70 to-black/80 backdrop-blur-lg rounded-xl border border-gray-700/30 hover:border-gray-600/50 transition-all duration-300 group shadow-md hover:shadow-lg hover:shadow-purple-500/10" style={{
                backgroundImage: `
                  repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px),
                  repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px),
                  radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.06) 0%, transparent 70%)
                `,
                backgroundSize: '12px 12px, 12px 12px, 80px 80px'
              }}>
                <ArrowLeft className="w-4 h-4 text-gray-300 group-hover:text-white transition-colors" />
                <span className="font-medium text-gray-300 group-hover:text-white transition-colors text-sm">Back to Dashboard</span>
              </Link>
              <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-black/80 via-gray-900/70 to-black/80 backdrop-blur-lg rounded-xl border border-gray-700/30 shadow-md" style={{
                backgroundImage: `
                  repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(255,255,255,0.02) 2px, rgba(255,255,255,0.02) 4px),
                  repeating-linear-gradient(-45deg, transparent, transparent 2px, rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px),
                  radial-gradient(circle at 70% 30%, rgba(59, 130, 246, 0.06) 0%, transparent 70%)
                `,
                backgroundSize: '12px 12px, 12px 12px, 80px 80px'
              }}>
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-purple-400" />
                <span className="font-semibold text-base sm:text-lg bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">ChatVerse</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto w-full pt-16 md:pt-18 lg:pt-20">
          <div className="text-center mb-8">
            <div className="relative inline-block mb-3">
              <h1 className="text-2xl md:text-3xl lg:text-4xl font-black mb-1 leading-tight bg-gradient-to-r from-white via-purple-100 to-blue-100 bg-clip-text text-transparent" style={{ fontFamily: 'Playfair Display, Georgia, serif' }}>
                Choose Your Plan
              </h1>
              <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-20 h-0.5 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"></div>
            </div>
            <p className="text-gray-300 text-sm sm:text-base max-w-xl mx-auto leading-relaxed mb-4">
              Flexible pricing plans for AI-powered automation
            </p>

            <div className="flex items-center justify-center gap-4 mb-6">
              <span className={`text-sm font-medium ${billingCycle === 'monthly' ? 'text-white' : 'text-gray-400'}`}>Monthly</span>
              <button
                onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                className={`relative w-14 h-7 rounded-full transition-all duration-300 ${billingCycle === 'yearly' ? 'bg-gradient-to-r from-purple-500 to-blue-500' : 'bg-gray-600'}`}
              >
                <div className={`absolute w-5 h-5 bg-white rounded-full top-1 transition-transform duration-300 ${billingCycle === 'yearly' ? 'translate-x-8' : 'translate-x-1'}`}></div>
              </button>
              <div className="flex items-center gap-2">
                <span className={`text-sm font-medium ${billingCycle === 'yearly' ? 'text-white' : 'text-gray-400'}`}>Yearly</span>
                {billingCycle === 'yearly' && (
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                    Save 20%
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-12 max-w-6xl mx-auto">
            {plans.map((plan) => {
              const isCurrentPlan = userProfile?.plan_id === plan.id;
              
              return (
              <div
                key={plan.id}
                className={`relative p-4 sm:p-6 rounded-2xl transition-all duration-500 group w-full pricing-card ${
                  plan.popular ? 'popular' : plan.premium ? 'premium' : ''
                }`}
              >
                <div className="fabric-overlay"></div>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
                      Most Popular
                    </div>
                  </div>
                )}

                {plan.premium && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg">
                      Enterprise
                    </div>
                  </div>
                )}

                <div className="text-center mb-4 sm:mb-6">
                  <div className={`w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br ${plan.gradient} rounded-xl flex items-center justify-center mx-auto mb-2 sm:mb-3 shadow-xl group-hover:scale-110 transition-transform duration-300`}>
                    <plan.icon className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                  </div>
                  <h3 className="text-lg sm:text-xl font-bold text-white mb-1 sm:mb-2">{plan.name}</h3>
                  <p className="text-gray-400 text-xs leading-relaxed px-2">{plan.description}</p>
                </div>

                <div className="text-center mb-4 sm:mb-6">
                  <div className="flex items-baseline justify-center gap-1 mb-2">
                    <span className="text-2xl sm:text-3xl font-bold text-white">${plan.price}</span>
                    <span className="text-gray-400 text-sm sm:text-base">{plan.period}</span>
                  </div>
                  {plan.originalPrice && (
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-gray-500 line-through text-sm">${plan.originalPrice}/year</span>
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                        Save ${plan.originalPrice - plan.price}
                      </span>
                    </div>
                  )}
                  <div className="mt-2 sm:mt-3 p-2 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-center justify-center gap-2">
                      <Rocket className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400" />
                      <span className="text-white font-medium text-xs sm:text-sm">{plan.credits.toLocaleString()} Credits</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">per {billingCycle === 'monthly' ? 'month' : 'year'}</p>
                  </div>
                </div>

                <div className="mb-4 sm:mb-6">
                  <h4 className="text-white font-medium mb-2 sm:mb-3 text-sm">Everything included:</h4>
                  <ul className="space-y-1 sm:space-y-2">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <Check className="w-3 h-3 sm:w-4 sm:h-4 text-green-400 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-300 text-xs leading-relaxed">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handlePlanSelect(plan.id)}
                  disabled={isCurrentPlan || processingPlanId === plan.id}
                  className={`w-full py-3 sm:py-4 px-4 sm:px-6 rounded-2xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 text-sm sm:text-base relative z-10 ${
                    isCurrentPlan
                      ? 'bg-gray-700 cursor-not-allowed text-gray-400'
                      : `fabric-btn ${plan.popular ? 'popular' : plan.premium ? 'premium' : ''} text-white cursor-pointer`
                  } ${processingPlanId === plan.id ? 'opacity-60 cursor-not-allowed' : ''}`}
                >
                  {isCurrentPlan ? 'Current Plan' : (processingPlanId === plan.id ? 'Processing…' : plan.buttonText)}
                  {!isCurrentPlan && processingPlanId !== plan.id && <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4" />}
                </button>
              </div>
            )})}
          </div>

          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">Frequently Asked Questions</h2>
            <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
              <div className="p-4 sm:p-6 bg-white/5 rounded-2xl border border-white/10">
                <h3 className="text-white font-semibold mb-2 text-sm sm:text-base">What are credits?</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Credits are used for AI automation tasks. Each query, post generation, or automation action consumes credits based on complexity.</p>
              </div>
              <div className="p-4 sm:p-6 bg-white/5 rounded-2xl border border-white/10">
                <h3 className="text-white font-semibold mb-2 text-sm sm:text-base">Can I change plans anytime?</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately with prorated billing.</p>
              </div>
              <div className="p-4 sm:p-6 bg-white/5 rounded-2xl border border-white/10">
                <h3 className="text-white font-semibold mb-2 text-sm sm:text-base">Is there a free trial?</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Professional and Enterprise plans come with a 14-day free trial. No credit card required to start.</p>
              </div>
              <div className="p-4 sm:p-6 bg-white/5 rounded-2xl border border-white/10">
                <h3 className="text-white font-semibold mb-2 text-sm sm:text-base">What happens if I exceed my credits?</h3>
                <p className="text-gray-400 text-xs sm:text-sm">You can purchase additional credit packs or upgrade to a higher plan. Automations pause when credits run out.</p>
              </div>
            </div>
          </div>

          <div className="text-center">
            <div className="p-6 sm:p-8 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-3xl border border-purple-500/20">
              <h3 className="text-xl sm:text-2xl font-bold text-white mb-3 sm:mb-4">Need a Custom Solution?</h3>
              <p className="text-gray-300 mb-4 sm:mb-6 max-w-2xl mx-auto text-sm sm:text-base px-2">
                Have specific requirements or need more than our Enterprise plan offers? Let's discuss a custom solution tailored to your needs.
              </p>
              <button className="fabric-btn popular px-6 sm:px-8 py-3 sm:py-4 rounded-2xl font-semibold transition-all duration-300 shadow-lg text-sm sm:text-base text-white">
                Contact Our Team
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;