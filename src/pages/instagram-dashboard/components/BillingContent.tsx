import React from 'react';
import { CreditCard, Download, Calendar, DollarSign, Package, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const BillingContent: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">Billing</h1>
          <p className="text-[#8e8e8e] mt-1">Manage your subscription, billing information, and payment history.</p>
        </div>
        <button onClick={() => navigate('/pricing')} className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#833ab4] to-[#fd1d1d] text-white rounded-lg hover:opacity-90 transition-opacity">
          <Package className="w-4 h-4" />
          <span>Upgrade Plan</span>
        </button>
      </div>

      {/* Current Plan */}
      <div className="p-6 bg-gradient-to-r from-[#833ab4]/10 to-[#fd1d1d]/10 border border-[#fd1d1d]/20 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Star className="w-6 h-6 text-[#fd1d1d]" />
            <h3 className="text-xl font-semibold text-white">Pro Plan</h3>
          </div>
          <div className="px-3 py-1 bg-[#fd1d1d]/20 text-[#fd1d1d] rounded-full text-sm">
            Active
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-2xl font-bold text-white">$29.99</p>
            <p className="text-sm text-[#8e8e8e]">per month</p>
          </div>
          <div>
            <p className="text-lg font-semibold text-white">Next billing</p>
            <p className="text-sm text-[#8e8e8e]">January 15, 2025</p>
          </div>
          <div>
            <p className="text-lg font-semibold text-white">Auto-renewal</p>
            <p className="text-sm text-green-400">Enabled</p>
          </div>
        </div>
      </div>

      {/* Billing Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: DollarSign, label: 'Total Spent', value: '$359.88', color: 'text-green-400' },
          { icon: Calendar, label: 'Billing Cycle', value: 'Monthly', color: 'text-blue-400' },
          { icon: CreditCard, label: 'Payment Method', value: '•••• 4242', color: 'text-purple-400' },
          { icon: Download, label: 'Invoices', value: '12', color: 'text-orange-400' },
        ].map((item, index) => (
          <div key={index} className="p-4 bg-[#1a1a1a] border border-[#262626] rounded-xl">
            <div className="flex items-center gap-3 mb-3">
              <item.icon className={`w-5 h-5 ${item.color}`} />
              <span className="text-sm text-[#8e8e8e]">{item.label}</span>
            </div>
            <p className="text-lg font-semibold text-white">{item.value}</p>
          </div>
        ))}
      </div>

      {/* Payment History */}
      <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Payment History</h3>
          <button className="flex items-center gap-2 px-3 py-2 bg-[#262626] text-white rounded-lg hover:bg-[#333] transition-colors">
            <Download className="w-4 h-4" />
            <span className="text-sm">Download All</span>
          </button>
        </div>
        
        <div className="space-y-3">
          {[
            { date: 'Dec 15, 2024', amount: '$29.99', status: 'Paid', invoice: 'INV-001' },
            { date: 'Nov 15, 2024', amount: '$29.99', status: 'Paid', invoice: 'INV-002' },
            { date: 'Oct 15, 2024', amount: '$29.99', status: 'Paid', invoice: 'INV-003' },
            { date: 'Sep 15, 2024', amount: '$29.99', status: 'Paid', invoice: 'INV-004' },
          ].map((payment, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-[#0a0a0a] rounded-lg">
              <div className="flex items-center gap-4">
                <div>
                  <p className="text-sm font-medium text-white">{payment.invoice}</p>
                  <p className="text-xs text-[#8e8e8e]">{payment.date}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm font-semibold text-white">{payment.amount}</span>
                <span className="px-2 py-1 bg-green-400/10 text-green-400 rounded-full text-xs">
                  {payment.status}
                </span>
                <button className="p-1 text-[#8e8e8e] hover:text-white transition-colors">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Payment Method */}
      <div className="p-6 bg-[#1a1a1a] border border-[#262626] rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">Payment Method</h3>
        <div className="flex items-center justify-between p-4 bg-[#0a0a0a] rounded-lg">
          <div className="flex items-center gap-3">
            <CreditCard className="w-6 h-6 text-[#8e8e8e]" />
            <div>
              <p className="text-sm font-medium text-white">•••• •••• •••• 4242</p>
              <p className="text-xs text-[#8e8e8e]">Expires 12/26</p>
            </div>
          </div>
          <button className="px-3 py-2 bg-[#262626] text-white rounded-lg hover:bg-[#333] transition-colors text-sm">
            Update
          </button>
        </div>
      </div>
    </div>
  );
};

export default BillingContent;