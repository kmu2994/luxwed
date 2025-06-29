import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const chatEndRef = useRef(null);

  // Initialize app
  useEffect(() => {
    fetchVendors();
    // Create a temporary user for demo
    createDemoUser();
  }, []);

  const createDemoUser = async () => {
    try {
      const response = await axios.post(`${API}/users`, {
        name: "Demo User",
        email: "demo@example.com", 
        phone: "+91 9999999999",
        role: "customer",
        preferences: {
          budget: 500000,
          location: "Mumbai",
          style_preference: "Modern",
          guest_count: 200
        }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error creating demo user:', error);
    }
  };

  const fetchVendors = async (category = null) => {
    try {
      const params = category && category !== 'all' ? { category } : {};
      const response = await axios.get(`${API}/vendors`, { params });
      setVendors(response.data);
    } catch (error) {
      console.error('Error fetching vendors:', error);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !user) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API}/chat`, {
        user_id: user.id,
        message: chatInput,
        session_id: sessionId || undefined
      });

      const aiMessage = { 
        role: 'assistant', 
        content: response.data.response,
        webSearchUsed: response.data.web_search_used
      };
      setChatMessages(prev => [...prev, aiMessage]);
      
      if (response.data.session_id && !sessionId) {
        setSessionId(response.data.session_id);
      }
      
    } catch (error) {
      console.error('Error sending chat message:', error);
      const errorMessage = { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' };
      setChatMessages(prev => [...prev, errorMessage]);
    }
    
    setChatInput('');
    setIsLoading(false);
  };

  const sendInquiry = async (vendorId) => {
    if (!user) return;
    
    try {
      await axios.post(`${API}/inquiries`, {
        user_id: user.id,
        vendor_id: vendorId,
        message: "I'm interested in your wedding services. Please share more details about packages and availability."
      });
      alert('Inquiry sent successfully! The vendor will contact you soon.');
    } catch (error) {
      console.error('Error sending inquiry:', error);
      alert('Error sending inquiry. Please try again.');
    }
  };

  const handleCategoryFilter = (category) => {
    setSelectedCategory(category);
    fetchVendors(category);
  };

  // Auto scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const categories = ['all', 'Photography', 'Catering', 'Venue', 'Decoration', 'Music', 'Transportation'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-100">
      {/* Navigation */}
      <nav className="bg-white shadow-lg border-b-4 border-rose-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-rose-600 to-pink-600 bg-clip-text text-transparent">
                  💒 WeddingAI
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentPage('home')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 'home' 
                    ? 'bg-rose-500 text-white shadow-lg transform scale-105' 
                    : 'text-rose-600 hover:bg-rose-100'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentPage('vendors')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 'vendors' 
                    ? 'bg-rose-500 text-white shadow-lg transform scale-105' 
                    : 'text-rose-600 hover:bg-rose-100'
                }`}
              >
                Vendors
              </button>
              <button
                onClick={() => setCurrentPage('chat')}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  currentPage === 'chat' 
                    ? 'bg-rose-500 text-white shadow-lg transform scale-105' 
                    : 'text-rose-600 hover:bg-rose-100'
                }`}
              >
                AI Planner
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Home Page */}
      {currentPage === 'home' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Plan Your Dream Wedding with 
              <span className="block bg-gradient-to-r from-rose-600 to-pink-600 bg-clip-text text-transparent">
                AI-Powered Intelligence
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              India's first zero-commission wedding platform with AI-powered vendor matching, 
              transparent pricing, and personalized planning assistance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => setCurrentPage('chat')}
                className="bg-gradient-to-r from-rose-500 to-pink-500 text-white px-8 py-4 rounded-xl font-semibold hover:from-rose-600 hover:to-pink-600 transform hover:scale-105 transition-all shadow-lg"
              >
                Start Planning with AI 🤖
              </button>
              <button 
                onClick={() => setCurrentPage('vendors')}
                className="bg-white text-rose-600 px-8 py-4 rounded-xl font-semibold border-2 border-rose-300 hover:bg-rose-50 transform hover:scale-105 transition-all shadow-lg"
              >
                Browse Vendors 💼
              </button>
            </div>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white p-8 rounded-2xl shadow-xl border border-rose-100 hover:shadow-2xl transition-all transform hover:-translate-y-2">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">AI Wedding Planner</h3>
              <p className="text-gray-600">
                Get personalized recommendations, budget planning, and timeline management with our advanced AI assistant.
              </p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-xl border border-rose-100 hover:shadow-2xl transition-all transform hover:-translate-y-2">
              <div className="text-4xl mb-4">💰</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Zero Commission</h3>
              <p className="text-gray-600">
                Unlike other platforms, we charge 0% commission. Save 15-25% on your wedding costs with transparent pricing.
              </p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-xl border border-rose-100 hover:shadow-2xl transition-all transform hover:-translate-y-2">
              <div className="text-4xl mb-4">⭐</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Verified Vendors</h3>
              <p className="text-gray-600">
                All vendors are verified with real reviews and ratings. Connect directly with top-rated wedding professionals.
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white p-8 rounded-2xl shadow-xl border border-rose-100 text-center">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div>
                <div className="text-3xl font-bold text-rose-600">500+</div>
                <div className="text-gray-600">Verified Vendors</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-rose-600">2000+</div>
                <div className="text-gray-600">Happy Couples</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-rose-600">₹25L</div>
                <div className="text-gray-600">Average Savings</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-rose-600">4.9⭐</div>
                <div className="text-gray-600">Platform Rating</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vendors Page */}
      {currentPage === 'vendors' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Wedding Vendors</h2>
            <p className="text-gray-600 mb-6">
              Discover verified wedding professionals with transparent pricing and zero commission fees.
            </p>
            
            {/* Category Filter */}
            <div className="flex flex-wrap gap-3 mb-6">
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => handleCategoryFilter(category)}
                  className={`px-4 py-2 rounded-full font-medium transition-all ${
                    selectedCategory === category
                      ? 'bg-rose-500 text-white shadow-lg'
                      : 'bg-white text-rose-600 border border-rose-300 hover:bg-rose-50'
                  }`}
                >
                  {category === 'all' ? 'All Categories' : category}
                </button>
              ))}
            </div>
          </div>

          {/* Vendors Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {vendors.map(vendor => (
              <div key={vendor.id} className="bg-white rounded-2xl shadow-xl border border-rose-100 overflow-hidden hover:shadow-2xl transition-all transform hover:-translate-y-1">
                <div className="h-48 bg-gradient-to-br from-rose-100 to-pink-100 flex items-center justify-center">
                  <div className="text-6xl">
                    {vendor.category === 'Photography' && '📸'}
                    {vendor.category === 'Catering' && '🍽️'}
                    {vendor.category === 'Venue' && '🏛️'}
                    {vendor.category === 'Decoration' && '🌸'}
                    {vendor.category === 'Music' && '🎵'}
                    {vendor.category === 'Transportation' && '🚗'}
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="bg-rose-100 text-rose-600 px-3 py-1 rounded-full text-sm font-medium">
                      {vendor.category}
                    </span>
                    {vendor.verified && (
                      <span className="text-green-500 text-sm font-medium">✓ Verified</span>
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{vendor.business_name}</h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{vendor.description}</p>
                  
                  <div className="flex items-center mb-3">
                    <span className="text-yellow-400">⭐</span>
                    <span className="text-sm font-medium text-gray-700 ml-1">
                      {vendor.rating} ({vendor.total_reviews} reviews)
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <div className="text-sm text-gray-500 mb-1">Pricing Range</div>
                    <div className="text-lg font-bold text-rose-600">
                      ₹{vendor.pricing_range.min.toLocaleString()} - ₹{vendor.pricing_range.max.toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="text-sm text-gray-500 mb-2">Services</div>
                    <div className="flex flex-wrap gap-1">
                      {vendor.services.slice(0, 3).map((service, idx) => (
                        <span key={idx} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => sendInquiry(vendor.id)}
                      className="flex-1 bg-rose-500 text-white py-2 px-4 rounded-lg font-medium hover:bg-rose-600 transition-colors"
                    >
                      Send Inquiry
                    </button>
                    <button className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Chat Page */}
      {currentPage === 'chat' && (
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-2xl shadow-xl border border-rose-100 overflow-hidden">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-rose-500 to-pink-500 p-6 text-white">
              <h2 className="text-2xl font-bold">AI Wedding Planner 🤖</h2>
              <p className="text-rose-100">
                Your personal wedding planning assistant. Ask about budget, vendors, timeline, or anything wedding-related!
              </p>
            </div>

            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto p-6 bg-gray-50">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <div className="text-6xl mb-4">💒</div>
                  <p className="text-lg mb-4">Welcome to your AI Wedding Planner!</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                    <button
                      onClick={() => setChatInput("What are the current wedding photography prices in Mumbai for 2025?")}
                      className="p-3 bg-white rounded-lg border border-rose-200 hover:border-rose-300 text-left transition-colors"
                    >
                      🌐 Get current market prices
                    </button>
                    <button
                      onClick={() => setChatInput("What are the latest wedding trends for 2025?")}
                      className="p-3 bg-white rounded-lg border border-rose-200 hover:border-rose-300 text-left transition-colors"
                    >
                      ✨ Latest 2025 wedding trends
                    </button>
                    <button
                      onClick={() => setChatInput("Find me real-time vendor availability in Delhi")}
                      className="p-3 bg-white rounded-lg border border-rose-200 hover:border-rose-300 text-left transition-colors"
                    >
                      🔍 Real-time vendor search
                    </button>
                    <button
                      onClick={() => setChatInput("What's the weather like for outdoor weddings this season?")}
                      className="p-3 bg-white rounded-lg border border-rose-200 hover:border-rose-300 text-left transition-colors"
                    >
                      🌤️ Weather & seasonal advice
                    </button>
                  </div>
                </div>
              )}
              
              {chatMessages.map((message, index) => (
                <div key={index} className={`mb-4 flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl p-4 rounded-2xl ${
                    message.role === 'user' 
                      ? 'bg-rose-500 text-white ml-4' 
                      : 'bg-white border border-rose-200 mr-4'
                  }`}>
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">
                        {message.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="flex-1">
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        {message.role === 'assistant' && message.webSearchUsed && (
                          <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
                            <span className="animate-pulse">🌐</span>
                            <span>Real-time web data used</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start mb-4">
                  <div className="bg-white border border-rose-200 p-4 rounded-2xl mr-4">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">🤖</div>
                      <div className="flex flex-col">
                        <div className="flex space-x-1 mb-1">
                          <div className="w-2 h-2 bg-rose-300 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-rose-300 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-rose-300 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <div className="text-xs text-gray-500 flex items-center gap-1">
                          <span className="animate-pulse">🌐</span>
                          <span>Searching web for latest info...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-6 border-t border-rose-100">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask me anything about wedding planning..."
                  className="flex-1 p-3 border border-rose-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent"
                  disabled={isLoading}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={isLoading || !chatInput.trim()}
                  className="bg-rose-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-rose-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;