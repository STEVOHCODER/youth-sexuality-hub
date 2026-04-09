import React, { useState, useEffect } from 'react';
import { 
  BookOpen, PlayCircle, Award, User, Search, 
  Settings, Bell, Clock, ChevronRight, CheckCircle,
  Star, Menu, ArrowLeft, Play, Pause, Volume2, Maximize,
  Compass, BarChart, Zap, Shield, Sparkles, LogIn, LogOut, Video
} from 'lucide-react';

// --- MOCK DATA ---
const COURSES = [
  {
    id: 1,
    title: "Generative AI & LLM Engineering",
    instructor: "Dr. Sarah Lin",
    role: "Former Lead AI at TechCorp",
    duration: "18h 45m",
    thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=1000",
    category: "Artificial Intelligence",
    progress: 34,
    rating: 4.9,
    students: "12.4k",
    enrolled: true,
    modules: [
      { title: "Attention Mechanisms & Transformers", duration: "1h 15m", completed: true },
      { title: "Fine-Tuning Open Source Models", duration: "2h 30m", completed: false },
      { title: "RAG Architecture Implementation", duration: "3h 00m", completed: false },
      { title: "Deploying to Production", duration: "1h 45m", completed: false }
    ]
  },
  {
    id: 2,
    title: "Advanced React Patterns & Next.js",
    instructor: "Marcus Doe",
    role: "Senior Frontend Architect",
    duration: "22h 10m",
    thumbnail: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&q=80&w=1000",
    category: "Web Development",
    progress: 0,
    rating: 4.8,
    students: "8.2k",
    enrolled: false,
    modules: [
      { title: "Server Components Deep Dive", duration: "50m", completed: false },
      { title: "State Management at Scale", duration: "2h 10m", completed: false },
      { title: "Performance Optimization", duration: "1h 30m", completed: false }
    ]
  },
  {
    id: 3,
    title: "Financial Modeling for Tech Startups",
    instructor: "Elena Rostova",
    role: "VC Partner at Vertex Capital",
    duration: "12h 00m",
    thumbnail: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=1000",
    category: "Business",
    progress: 100,
    rating: 4.9,
    students: "5.1k",
    enrolled: true,
    modules: [
      { title: "Unit Economics", duration: "1h 20m", completed: true },
      { title: "Forecasting Revenue", duration: "2h 00m", completed: true },
      { title: "Valuation Methods", duration: "1h 15m", completed: true }
    ]
  }
];

export default function NexusLearningPlatform() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'dashboard', 'player'
  const [selectedCourse, setSelectedCourse] = useState(null);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('landing');
  };

  const openCourse = (course) => {
    setSelectedCourse(course);
    setCurrentView('player');
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-violet-200">
      
      {/* GLOBAL NAVBAR */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div 
            className="flex items-center space-x-3 cursor-pointer group" 
            onClick={() => isAuthenticated ? setCurrentView('dashboard') : setCurrentView('landing')}
          >
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center group-hover:rotate-12 transition-transform duration-300 shadow-lg shadow-slate-900/20">
              <Zap size={20} className="text-white fill-current" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-slate-900">Nexus<span className="text-violet-600">Edu</span></span>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors">Catalog</a>
            <a href="#" className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors">Masterclasses</a>
            <a href="#" className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors">Enterprise</a>
          </div>

          <div>
            {!isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <button onClick={handleLogin} className="text-sm font-bold text-slate-700 hover:text-slate-900 transition-colors hidden sm:block">
                  Sign In
                </button>
                <button onClick={handleLogin} className="bg-slate-900 text-white text-sm font-bold px-6 py-2.5 rounded-full hover:bg-slate-800 transition-all shadow-md hover:shadow-xl hover:-translate-y-0.5 flex items-center">
                  Start Learning <ArrowLeft size={16} className="ml-2 rotate-180" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-5">
                <button className="relative text-slate-400 hover:text-slate-700 transition-colors">
                  <Bell size={22} />
                  <span className="absolute 0 right-0 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white"></span>
                </button>
                <div className="h-8 w-px bg-slate-200"></div>
                <div className="flex items-center space-x-3 group cursor-pointer" onClick={handleLogout}>
                  <img src="https://i.pravatar.cc/150?img=68" alt="Profile" className="w-10 h-10 rounded-full border-2 border-slate-100 group-hover:border-violet-200 transition-colors" />
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-bold leading-none">David Kim</p>
                    <p className="text-xs text-violet-600 font-semibold mt-1 flex items-center">Log out <LogOut size={10} className="ml-1"/></p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="pt-20">
        {currentView === 'landing' && <LandingPage onLogin={handleLogin} />}
        {currentView === 'dashboard' && <DashboardView courses={COURSES} onOpenCourse={openCourse} />}
        {currentView === 'player' && selectedCourse && <CoursePlayer course={selectedCourse} onBack={() => setCurrentView('dashboard')} />}
      </div>
      
    </div>
  );
}

/* =========================================
   1. LANDING PAGE VIEW
========================================= */
function LandingPage({ onLogin }) {
  return (
    <div className="animate-in fade-in duration-700">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-slate-900 pt-24 pb-32">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 -translate-y-12 translate-x-1/3 w-[800px] h-[800px] bg-violet-600/20 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 translate-y-1/3 -translate-x-1/3 w-[600px] h-[600px] bg-emerald-500/20 rounded-full blur-[120px] pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="text-left">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-white/5 border border-white/10 text-violet-300 text-sm font-semibold mb-8 backdrop-blur-sm">
                <Sparkles size={16} className="mr-2" /> Voted #1 Tech Learning Platform 2024
              </div>
              <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight leading-[1.1] mb-6">
                Master the skills of <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-emerald-400">tomorrow.</span>
              </h1>
              <p className="text-lg md:text-xl text-slate-300 mb-10 max-w-lg leading-relaxed">
                Learn directly from industry leaders at top tech companies. High-production masterclasses designed to accelerate your career.
              </p>
              <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                <button onClick={onLogin} className="bg-white text-slate-900 font-bold px-8 py-4 rounded-full hover:bg-slate-100 transition-all shadow-[0_0_40px_-10px_rgba(255,255,255,0.3)] flex items-center justify-center text-lg">
                  Explore Catalog <ChevronRight size={20} className="ml-2" />
                </button>
                <button className="bg-white/5 text-white border border-white/10 font-bold px-8 py-4 rounded-full hover:bg-white/10 transition-all flex items-center justify-center text-lg backdrop-blur-sm">
                  <PlayCircle size={20} className="mr-2" /> Watch Demo
                </button>
              </div>
              
              <div className="mt-12 flex items-center space-x-6 text-slate-400 text-sm font-semibold">
                <div className="flex -space-x-3">
                  {[1,2,3,4].map(i => (
                    <img key={i} src={`https://i.pravatar.cc/150?img=${i+10}`} className="w-10 h-10 rounded-full border-2 border-slate-900" alt="Student" />
                  ))}
                </div>
                <p>Over <span className="text-white">500,000+</span> professionals enrolled</p>
              </div>
            </div>
            
            {/* Hero Image / Video Mockup */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl shadow-violet-900/20 border border-white/10 bg-slate-800">
                <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&q=80&w=1200" alt="Learning" className="w-full h-auto opacity-80" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center cursor-pointer hover:scale-110 transition-transform hover:bg-white/30 border border-white/30">
                    <Play size={32} className="text-white fill-current ml-2" />
                  </div>
                </div>
              </div>
              
              {/* Floating Badge */}
              <div className="absolute -bottom-6 -left-6 bg-white rounded-2xl p-4 shadow-xl shadow-slate-900/10 border border-slate-100 flex items-center space-x-4 animate-bounce" style={{ animationDuration: '3s' }}>
                <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-emerald-600">
                  <Shield size={24} />
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-900">Certified Experts</p>
                  <p className="text-xs text-slate-500 font-medium">Top 1% Instructors</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Logos Section */}
      <div className="bg-white py-10 border-b border-slate-200/50">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm font-bold text-slate-400 mb-6 tracking-widest uppercase">Learn skills used at</p>
          <div className="flex flex-wrap justify-center gap-12 opacity-50 grayscale">
            {['Google', 'Microsoft', 'Netflix', 'Spotify', 'Stripe'].map(logo => (
               <div key={logo} className="text-2xl font-black">{logo}</div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Featured Courses (Preview) */}
      <div className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Trending Masterclasses</h2>
              <p className="text-slate-600 text-lg">Curated programs to accelerate your growth.</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {COURSES.map(course => (
              <CourseCard key={course.id} course={course} onClick={onLogin} isPublic />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =========================================
   2. DASHBOARD VIEW
========================================= */
function DashboardView({ courses, onOpenCourse }) {
  const activeCourse = courses.find(c => c.enrolled && c.progress < 100);
  const myCourses = courses.filter(c => c.enrolled);
  
  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      <div className="flex flex-col lg:flex-row gap-8 mb-12">
        {/* Welcome Banner */}
        <div className="flex-1 bg-slate-900 rounded-[2rem] p-8 md:p-10 text-white relative overflow-hidden shadow-xl shadow-slate-900/10">
          <div className="absolute top-0 right-0 w-64 h-64 bg-violet-500/30 rounded-full blur-3xl -translate-y-10 translate-x-10"></div>
          
          <div className="relative z-10">
            <h1 className="text-3xl md:text-4xl font-bold mb-2">Welcome back, David! 👋</h1>
            <p className="text-slate-300 text-lg mb-8 max-w-md">You're on a 5-day streak. Keep up the momentum and finish your AI Engineering module today.</p>
            
            {activeCourse && (
              <div className="bg-white/10 backdrop-blur-md border border-white/10 rounded-2xl p-5 flex items-center justify-between group cursor-pointer hover:bg-white/20 transition-all" onClick={() => onOpenCourse(activeCourse)}>
                <div className="flex items-center space-x-4">
                  <div className="w-14 h-14 rounded-xl overflow-hidden shrink-0">
                    <img src={activeCourse.thumbnail} alt="" className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <p className="text-xs text-violet-300 font-bold mb-1 uppercase tracking-wider">Up Next</p>
                    <h3 className="font-bold text-white text-lg leading-tight group-hover:text-violet-200 transition-colors">{activeCourse.modules[1].title}</h3>
                  </div>
                </div>
                <button className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-slate-900 shrink-0 shadow-lg group-hover:scale-110 transition-transform">
                  <Play size={20} className="fill-current ml-1" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats Bento Box */}
        <div className="lg:w-80 grid grid-cols-2 gap-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mb-4">
              <CheckCircle size={20} />
            </div>
            <div>
              <p className="text-3xl font-black text-slate-900 mb-1">1</p>
              <p className="text-sm font-semibold text-slate-500">Course<br/>Completed</p>
            </div>
          </div>
          <div className="bg-white rounded-3xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center text-amber-600 mb-4">
              <Star size={20} />
            </div>
            <div>
              <p className="text-3xl font-black text-slate-900 mb-1">320</p>
              <p className="text-sm font-semibold text-slate-500">Total<br/>Points</p>
            </div>
          </div>
          <div className="col-span-2 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-3xl p-6 text-white flex items-center justify-between shadow-lg shadow-violet-200 cursor-pointer hover:opacity-95 transition-opacity">
            <div>
              <p className="text-sm font-bold text-violet-200 mb-1">Weekly Goal</p>
              <p className="text-xl font-bold">12 / 15 Hours</p>
            </div>
            <div className="relative w-14 h-14">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="28" cy="28" r="24" stroke="rgba(255,255,255,0.2)" strokeWidth="6" fill="none" />
                <circle cx="28" cy="28" r="24" stroke="white" strokeWidth="6" fill="none" strokeDasharray="150" strokeDashoffset="30" strokeLinecap="round" className="transition-all duration-1000 ease-out" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-8 border-b border-slate-200 mb-8">
        <button className="pb-4 border-b-2 border-slate-900 text-slate-900 font-bold">My Learning</button>
        <button className="pb-4 border-b-2 border-transparent text-slate-500 font-semibold hover:text-slate-800">Saved</button>
        <button className="pb-4 border-b-2 border-transparent text-slate-500 font-semibold hover:text-slate-800">Certificates</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {myCourses.map(course => (
          <CourseCard key={course.id} course={course} onClick={() => onOpenCourse(course)} />
        ))}
      </div>
    </div>
  );
}

/* =========================================
   3. COURSE PLAYER VIEW
========================================= */
function CoursePlayer({ course, onBack }) {
  const [activeModule, setActiveModule] = useState(0);
  const currentMod = course.modules[activeModule];

  return (
    <div className="fixed inset-0 top-20 z-40 bg-white flex flex-col lg:flex-row animate-in fade-in slide-in-from-right-8 duration-300">
      
      {/* Video Section */}
      <div className="flex-1 bg-slate-950 flex flex-col relative">
        <button 
          onClick={onBack}
          className="absolute top-6 left-6 z-50 w-10 h-10 bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 rounded-full flex items-center justify-center text-white transition-all shadow-lg"
        >
          <ArrowLeft size={20} />
        </button>

        <div className="flex-1 relative group flex items-center justify-center overflow-hidden">
          <img src={course.thumbnail} alt="" className="absolute w-full h-full object-cover opacity-30 mix-blend-overlay pointer-events-none" />
          
          <div className="relative z-10 w-24 h-24 bg-violet-600/90 rounded-full flex items-center justify-center text-white cursor-pointer hover:bg-violet-500 hover:scale-110 transition-all shadow-[0_0_50px_rgba(124,58,237,0.5)] backdrop-blur-md">
            <Play size={40} className="fill-current ml-2" />
          </div>

          {/* Player Controls UI Simulator */}
          <div className="absolute bottom-0 w-full bg-gradient-to-t from-black via-black/80 to-transparent p-6 pt-24 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <div className="mb-4 text-white">
              <h3 className="font-bold text-lg">{activeModule + 1}. {currentMod.title}</h3>
              <p className="text-sm text-slate-400">{course.title}</p>
            </div>
            <div className="w-full bg-white/20 h-1.5 rounded-full mb-6 relative cursor-pointer group/bar">
              <div className="bg-violet-500 h-full rounded-full w-1/3 relative group-hover/bar:bg-violet-400 transition-colors">
                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow border-2 border-violet-500 opacity-0 group-hover/bar:opacity-100 transition-opacity"></div>
              </div>
            </div>
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-6">
                <button className="hover:text-violet-400 transition-colors"><Pause size={24} className="fill-current"/></button>
                <button className="hover:text-violet-400 transition-colors"><Video size={20} /></button>
                <div className="flex items-center space-x-2 hidden sm:flex">
                  <Volume2 size={20} />
                  <div className="w-20 h-1 bg-white/30 rounded-full"><div className="w-2/3 h-full bg-white rounded-full"></div></div>
                </div>
                <span className="text-sm font-medium tabular-nums hidden sm:block">12:04 / {currentMod.duration}</span>
              </div>
              <div className="flex items-center space-x-6">
                <button className="text-sm font-bold bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors">1.5x</button>
                <button className="hover:text-violet-400 transition-colors"><Settings size={20} /></button>
                <button className="hover:text-violet-400 transition-colors"><Maximize size={20} /></button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sidebar Syllabus */}
      <div className="w-full lg:w-[450px] bg-white border-l border-slate-200 flex flex-col h-[calc(100vh-80px)] overflow-y-auto">
        <div className="p-8 border-b border-slate-100 shrink-0">
          <div className="flex justify-between items-start mb-4">
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-violet-50 text-violet-700 text-xs font-bold uppercase tracking-wider">
              {course.category}
            </div>
            <div className="flex items-center text-amber-500 text-sm font-bold">
              <Star size={16} className="fill-current mr-1" /> {course.rating}
            </div>
          </div>
          <h2 className="text-2xl font-bold text-slate-900 leading-tight mb-2">{course.title}</h2>
          <p className="text-slate-500 font-medium flex items-center">
            <User size={16} className="mr-2"/> {course.instructor}
          </p>
          
          <div className="mt-8">
            <div className="flex justify-between text-sm font-bold mb-2">
              <span className="text-slate-700">Course Progress</span>
              <span className="text-violet-600">{course.progress}%</span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div className="bg-violet-600 h-full rounded-full transition-all duration-1000" style={{ width: `${course.progress}%` }}></div>
            </div>
          </div>
        </div>

        <div className="flex-1 p-6 bg-slate-50/50">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Course Material</h3>
          <div className="space-y-3">
            {course.modules.map((mod, idx) => {
              const isActive = activeModule === idx;
              return (
                <div 
                  key={idx} 
                  onClick={() => setActiveModule(idx)}
                  className={`flex p-4 rounded-2xl border transition-all cursor-pointer ${
                    isActive 
                      ? 'bg-white border-violet-200 shadow-md shadow-violet-100/50 ring-1 ring-violet-100' 
                      : mod.completed 
                        ? 'bg-slate-50 border-transparent hover:bg-slate-100 opacity-70' 
                        : 'bg-white border-slate-200 hover:border-violet-300 hover:shadow-sm'
                  }`}
                >
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 shrink-0 mt-0.5 ${
                    isActive ? 'bg-violet-100 text-violet-600' : mod.completed ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-400'
                  }`}>
                    {isActive ? <div className="w-3 h-3 bg-violet-600 rounded-full animate-pulse" /> : mod.completed ? <CheckCircle size={20} /> : <PlayCircle size={20} />}
                  </div>
                  <div className="flex-1">
                    <h4 className={`font-bold leading-snug mb-1 ${isActive ? 'text-violet-900' : mod.completed ? 'text-slate-600' : 'text-slate-900'}`}>
                      {idx + 1}. {mod.title}
                    </h4>
                    <p className="text-xs font-semibold text-slate-500 flex items-center">
                      <Clock size={12} className="mr-1" /> {mod.duration}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

/* =========================================
   REUSABLE UI COMPONENTS
========================================= */
function CourseCard({ course, onClick, isPublic = false }) {
  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-[2rem] p-3 border border-slate-200 hover:border-violet-300 overflow-hidden shadow-sm hover:shadow-2xl hover:shadow-violet-900/10 hover:-translate-y-1 transition-all duration-300 group cursor-pointer flex flex-col h-full"
    >
      <div className="relative h-60 overflow-hidden rounded-[1.5rem] shrink-0">
        <img 
          src={course.thumbnail} 
          alt={course.title} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-in-out"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/20 to-transparent"></div>
        
        <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-bold text-slate-900 shadow-lg">
          {course.category}
        </div>
        
        <div className="absolute bottom-4 left-4 right-4 flex items-end justify-between">
          <div>
            <p className="text-white font-bold flex items-center mb-0.5"><User size={14} className="mr-1.5" /> {course.instructor}</p>
            <p className="text-slate-300 text-xs font-medium">{course.role}</p>
          </div>
          {isPublic && (
            <div className="bg-white/20 backdrop-blur-md px-2 py-1 rounded-lg flex items-center text-xs font-bold text-white border border-white/20">
              <Star size={12} className="mr-1 fill-amber-400 text-amber-400" /> {course.rating}
            </div>
          )}
        </div>
      </div>

      <div className="p-5 flex flex-col flex-1">
        <h3 className="font-bold text-xl text-slate-900 leading-snug mb-4 group-hover:text-violet-600 transition-colors line-clamp-2">
          {course.title}
        </h3>
        
        <div className="mt-auto">
          <div className="flex items-center justify-between text-xs font-bold text-slate-500 mb-5 pb-5 border-b border-slate-100">
            <div className="flex items-center"><Clock size={16} className="mr-1.5 text-slate-400" /> {course.duration}</div>
            <div className="flex items-center"><BookOpen size={16} className="mr-1.5 text-slate-400" /> {course.modules.length} Modules</div>
            {isPublic && <div className="flex items-center"><User size={16} className="mr-1.5 text-slate-400" /> {course.students}</div>}
          </div>

          {!isPublic && course.enrolled ? (
            <div>
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className={course.progress > 0 ? "text-violet-600" : "text-slate-400"}>
                  {course.progress > 0 ? `${course.progress}% Completed` : 'Not Started'}
                </span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-violet-600 h-full rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${course.progress}%` }}
                ></div>
              </div>
            </div>
          ) : (
             <div className="flex items-center justify-between">
               <span className="font-black text-lg text-slate-900">$199</span>
               <button className="px-5 py-2.5 bg-slate-900 hover:bg-violet-600 text-white text-sm font-bold rounded-xl transition-colors">
                 Enroll Now
               </button>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
