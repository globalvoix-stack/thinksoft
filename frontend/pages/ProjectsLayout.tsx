import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import { ChevronDown, Gift, Zap, LogOut } from 'lucide-react';
import { SearchModal } from '../components/SearchModal';
// @ts-ignore
import logo from '../logo.png';

const CustomHome = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M3 10l9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><line x1="9" y1="16" x2="15" y2="16" />
  </svg>
);
const CustomSearch = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);
const CustomCompass = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
  </svg>
);
const CustomGrid = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="7" cy="7" r="3" /><circle cx="17" cy="7" r="3" /><circle cx="7" cy="17" r="3" /><circle cx="17" cy="17" r="3" />
  </svg>
);
const CustomStar = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
  </svg>
);
const CustomUser = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
  </svg>
);
const CustomUsers = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);
const CustomPanelLeft = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect width="18" height="18" x="3" y="3" rx="2" /><path d="M9 3v18" />
  </svg>
);

const Tooltip = ({ children, text, shortcut }: { children: React.ReactNode; text: string; shortcut?: string }) => (
  <div className="relative group/tooltip flex items-center justify-center">
    {children}
    <div className="absolute left-full ml-3 top-1/2 -translate-y-1/2 translate-x-[-4px] group-hover/tooltip:translate-x-0 px-3 py-2 bg-[#1e1e1e] text-[#eeeeee] text-[13px] font-medium rounded-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 delay-150 ease-out pointer-events-none whitespace-nowrap z-[200] flex items-center gap-2">
      {text}
      {shortcut && <span className="bg-[#333] px-1.5 py-0.5 rounded-md text-[11px] text-neutral-300 font-semibold tracking-wide">{shortcut}</span>}
    </div>
  </div>
);

const SidebarItem = ({ icon: Icon, label, active = false, badge = null, onClick }: any) => (
  <button onClick={onClick} className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-[13px] transition-colors ${active ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-neutral-800/30'}`}>
    <div className="flex items-center gap-3">
      {Icon && <Icon size={14} className="text-white" />}
      <span className="font-normal">{label}</span>
    </div>
    {badge && <span className="text-[9px] font-semibold bg-neutral-800 text-white px-1.5 py-0.5 rounded border border-neutral-700">{badge}</span>}
  </button>
);

const ProjectItem = ({ label }: { label: string }) => (
  <button className="w-full flex items-center gap-3 px-3 py-1.5 rounded-lg text-[13px] text-white hover:bg-neutral-800/30 transition-colors">
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white flex-shrink-0">
      <polygon points="12 2 22 12 12 22 2 12 12 2" />
    </svg>
    <span className="truncate font-normal">{label}</span>
  </button>
);

export type ActivePage = 'all-projects' | 'starred' | 'created-by-me' | 'shared-with-me';

interface ProjectsLayoutProps {
  activePage: ActivePage;
  children: React.ReactNode;
}

export default function ProjectsLayout({ activePage, children }: ProjectsLayoutProps) {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const firstName = user?.firstName || user?.username || user?.emailAddresses?.[0]?.emailAddress?.split('@')[0] || 'there';
  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setIsSearchOpen(true); }
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') { e.preventDefault(); setIsSidebarOpen(prev => !prev); }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, []);

  if (!isLoaded) return <div className="min-h-screen bg-[#171717] flex items-center justify-center"><div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" /></div>;
  if (!isSignedIn) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen bg-[#171717] text-white font-sans overflow-hidden">
      {isSearchOpen && <SearchModal onClose={() => setIsSearchOpen(false)} />}

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: isSidebarOpen ? 240 : 64 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="flex-shrink-0 relative z-50 h-full bg-[#171717]"
      >
        <AnimatePresence initial={false}>
          {isSidebarOpen ? (
            <motion.div key="open" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="absolute inset-0 w-full overflow-hidden">
              <div className="w-[240px] flex flex-col h-full">
                <div className="p-4 flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <img src={logo} alt="Logo" className="w-6 h-6 object-contain rounded-md" />
                    <button onClick={() => setIsSidebarOpen(false)} className="text-white transition-colors cursor-ew-resize"><CustomPanelLeft size={18} /></button>
                  </div>
                  <button className="flex items-center justify-between w-full px-3 py-2 bg-neutral-800/40 hover:bg-neutral-800/60 rounded-lg border border-neutral-700/50 transition-colors">
                    <div className="flex items-center gap-2">
                      {user?.imageUrl ? <img src={user.imageUrl} alt="Avatar" className="w-5 h-5 rounded object-cover" /> : <div className="w-5 h-5 rounded bg-orange-600 flex items-center justify-center text-[11px] font-bold text-white">{initials}</div>}
                      <span className="text-[13px] font-semibold text-white truncate max-w-[120px]">{firstName}'s Thinksoft</span>
                    </div>
                    <ChevronDown size={14} className="text-white" />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto hide-scrollbar px-2 pb-4 flex flex-col gap-6">
                  <div className="flex flex-col gap-0.5">
                    <SidebarItem icon={CustomHome} label="Home" onClick={() => navigate('/dashboard')} />
                    <SidebarItem icon={CustomSearch} label="Search" badge="Ctrl K" onClick={() => setIsSearchOpen(true)} />
                    <SidebarItem icon={CustomCompass} label="Resources" />
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <div className="px-3 py-2 text-[13px] font-semibold text-[#a3a3a3]">Projects</div>
                    <SidebarItem icon={CustomGrid} label="All projects" active={activePage === 'all-projects'} onClick={() => navigate('/all-projects')} />
                    <SidebarItem icon={CustomStar} label="Starred" active={activePage === 'starred'} onClick={() => navigate('/starred')} />
                    <SidebarItem icon={CustomUser} label="Created by me" active={activePage === 'created-by-me'} onClick={() => navigate('/created-by-me')} />
                    <SidebarItem icon={CustomUsers} label="Shared with me" active={activePage === 'shared-with-me'} onClick={() => navigate('/shared-with-me')} />
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <div className="px-3 py-2 text-[13px] font-semibold text-[#a3a3a3]">Recents</div>
                    {['Vibe Clone Studio','Landing Page Spark','SchoolDash Premium','Stream Central (82)','Stream Scene','Shop & Sign','Image Weaver','AI Launchpad'].map(n => <ProjectItem key={n} label={n} />)}
                  </div>
                </div>

                <div className="p-4 flex flex-col gap-2 border-t border-neutral-800/50">
                  <button className="flex items-center justify-between w-full p-3 bg-[#1c1c1c] hover:bg-[#252525] rounded-xl border border-white/5 transition-colors">
                    <div className="flex flex-col items-start gap-0.5">
                      <span className="text-[13px] font-semibold text-white">Share Thinksoft</span>
                      <span className="text-[11px] text-white">100 credits per paid referral</span>
                    </div>
                    <div className="w-7 h-7 rounded-full border border-white/10 flex items-center justify-center text-white"><Gift size={12} /></div>
                  </button>
                  <button className="flex items-center justify-between w-full p-3 bg-[#1c1c1c] hover:bg-[#252525] rounded-xl border border-white/5 transition-colors mt-1">
                    <div className="flex flex-col items-start gap-0.5">
                      <span className="text-[13px] font-semibold text-white">Upgrade to Pro</span>
                      <span className="text-[11px] text-white">Unlock more features</span>
                    </div>
                    <div className="w-7 h-7 rounded-full bg-[#2b2d42] flex items-center justify-center text-white"><Zap size={12} className="fill-white" /></div>
                  </button>
                  <div className="flex items-center justify-between mt-4 px-1">
                    {user?.imageUrl ? <img src={user.imageUrl} alt="Avatar" className="w-6 h-6 rounded-full object-cover" /> : <div className="w-6 h-6 rounded-full bg-[#5c9c49] flex items-center justify-center text-xs font-bold text-white">{initials}</div>}
                    <button onClick={() => signOut({ redirectUrl: '/' })} className="text-white transition-colors hover:text-red-400"><LogOut size={18} strokeWidth={1.5} /></button>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div key="closed" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="absolute inset-0 w-[64px] flex flex-col items-center py-5">
              <Tooltip text="Open sidebar" shortcut="Ctrl B">
                <button onClick={() => setIsSidebarOpen(true)} className="text-white mb-6 hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors cursor-ew-resize"><CustomPanelLeft size={16} /></button>
              </Tooltip>
              <div className="w-6 h-6 rounded-[5px] overflow-hidden mb-8 shadow-sm"><img src={logo} alt="Logo" className="w-full h-full object-cover" /></div>
              <div className="flex flex-col gap-2 w-full items-center">
                <Tooltip text="Home"><button onClick={() => navigate('/dashboard')} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomHome size={14} /></button></Tooltip>
                <Tooltip text="Open search (⌘K)"><button onClick={() => setIsSearchOpen(true)} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomSearch size={14} /></button></Tooltip>
                <Tooltip text="Resources"><button className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomCompass size={14} /></button></Tooltip>
              </div>
              <div className="flex flex-col gap-2 w-full items-center mt-6">
                <Tooltip text="All projects"><button onClick={() => navigate('/all-projects')} className={`w-9 h-9 flex items-center justify-center rounded-xl transition-colors ${activePage === 'all-projects' ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-[#333333]'}`}><CustomGrid size={14} /></button></Tooltip>
                <Tooltip text="Starred"><button onClick={() => navigate('/starred')} className={`w-9 h-9 flex items-center justify-center rounded-xl transition-colors ${activePage === 'starred' ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-[#333333]'}`}><CustomStar size={14} /></button></Tooltip>
                <Tooltip text="Created by me"><button onClick={() => navigate('/created-by-me')} className={`w-9 h-9 flex items-center justify-center rounded-xl transition-colors ${activePage === 'created-by-me' ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-[#333333]'}`}><CustomUser size={14} /></button></Tooltip>
                <Tooltip text="Shared with me"><button onClick={() => navigate('/shared-with-me')} className={`w-9 h-9 flex items-center justify-center rounded-xl transition-colors ${activePage === 'shared-with-me' ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-[#333333]'}`}><CustomUsers size={14} /></button></Tooltip>
              </div>
              <div className="mt-auto flex flex-col items-center gap-4">
                {user?.imageUrl ? <img src={user.imageUrl} alt="Avatar" className="w-7 h-7 rounded-full object-cover cursor-pointer hover:opacity-90" /> : <div className="w-7 h-7 rounded-full bg-[#5c9c49] flex items-center justify-center text-[13px] font-bold text-white cursor-pointer hover:opacity-90">{initials}</div>}
                <Tooltip text="Sign out">
                  <button onClick={() => signOut({ redirectUrl: '/' })} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors hover:text-red-400"><LogOut size={16} strokeWidth={1.5} /></button>
                </Tooltip>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 relative flex flex-col overflow-hidden rounded-[32px] bg-[#0d0d0d] m-3 ml-2 border border-white/5 shadow-2xl">
        {children}
      </div>
    </div>
  );
}
