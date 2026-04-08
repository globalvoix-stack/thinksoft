import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import {
  ChevronDown, Gift, Zap, LogOut,
  Search, MoreHorizontal, Plus, LayoutGrid, List, Check, Info, Star,
  Link2, ArrowUpRight, BarChart2, Edit2, Settings, Trash2, Layers, SquareDashed,
} from 'lucide-react';
import { SearchModal } from '../components/SearchModal';
// @ts-ignore
import logo from '../logo.png';

/* ─── Sidebar shared icons ─── */
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

const Tooltip = ({ children, text, shortcut, position = 'right' }: { children: React.ReactNode; text: string; shortcut?: string; position?: 'right' | 'top' }) => (
  <div className="relative group/tooltip flex items-center justify-center">
    {children}
    <div className={`absolute ${position === 'right' ? 'left-full ml-3 top-1/2 -translate-y-1/2 translate-x-[-4px] group-hover/tooltip:translate-x-0' : 'bottom-full mb-3 left-1/2 -translate-x-1/2 translate-y-[4px] group-hover/tooltip:translate-y-0'} px-3 py-2 bg-[#1e1e1e] text-[#eeeeee] text-[13px] font-medium rounded-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 delay-150 ease-out pointer-events-none whitespace-nowrap z-[200] flex items-center gap-2`}>
      {text}
      {shortcut && <span className="bg-[#333] px-1.5 py-0.5 rounded-md text-[11px] text-neutral-300 font-semibold tracking-wide">{shortcut}</span>}
    </div>
  </div>
);

const SidebarItem = ({ icon: Icon, label, active = false, badge = null, rightElement = null, onClick }: any) => (
  <button onClick={onClick} className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-[13px] transition-colors ${active ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-neutral-800/30'}`}>
    <div className="flex items-center gap-3">
      {Icon && <Icon size={14} className="text-white" />}
      <span className="font-normal">{label}</span>
    </div>
    {badge && <span className="text-[9px] font-semibold bg-neutral-800 text-white px-1.5 py-0.5 rounded border border-neutral-700">{badge}</span>}
    {rightElement}
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

/* ─── Projects data ─── */
const initialActiveProjects = [
  { id: 1, title: 'Stream Box', edited: 'Edited 43 minutes ago', createdAt: '18 hours ago', creator: 'Think', image: 'https://images.unsplash.com/photo-1616530940355-351fabd9524b?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
];
const initialInactiveProjects = [
  { id: 2, title: 'ClueMaster Game', edited: 'Edited 15 Jan 2026', createdAt: '4 Jan 2026', creator: 'Think', image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 3, title: 'Your Next Marketplace', edited: 'Edited 8 Jan 2026', createdAt: '29 Dec 2025', creator: 'Think', image: 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 4, title: 'Dynamic Page Clone', edited: 'Edited 8 Jan 2026', createdAt: '7 Jan 2026', creator: 'Think', image: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 5, title: 'Your Personal Search Engine', edited: 'Edited 4 Jan 2026', createdAt: '4 Jan 2026', creator: 'Think', image: 'https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 6, title: 'Your Next Binge', edited: 'Edited 4 Jan 2026', createdAt: '4 Jan 2026', creator: 'Think', image: 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 7, title: 'N Intro Stream', edited: 'Edited 1 Jan 2026', createdAt: '1 Jan 2026', creator: 'Think', image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
  { id: 8, title: 'Project Make It', edited: 'Edited 24 Nov 2025', createdAt: '24 Nov 2025', creator: 'Think', image: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?q=80&w=800&auto=format&fit=crop', avatar: 'T', avatarColor: 'bg-[#659b4a]' },
];

/* ─── Dropdown helpers ─── */
const SortDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setIsOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);
  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setIsOpen(!isOpen)} className={`flex items-center gap-2 bg-transparent hover:bg-white/5 text-[#e0e0e0] px-3.5 py-1.5 rounded-lg text-[13px] font-medium transition-colors border ${isOpen ? 'border-[#555] bg-white/5' : 'border-white/20'}`}>
        Last edited <ChevronDown className="w-4 h-4 text-[#a0a0a0] ml-1" />
      </button>
      {isOpen && (
        <div className="absolute top-full left-0 mt-1.5 w-[200px] bg-[#1a1a1a] border border-[#333] rounded-xl shadow-xl overflow-hidden z-50 py-1.5">
          <div className="px-4 py-2"><span className="text-[#888] text-[13px] font-medium">Sort by</span></div>
          {['Last edited','Last viewed','Created','Name'].map(o => (
            <button key={o} className="flex items-center justify-between w-full px-4 py-2 text-left hover:bg-white/5 transition-colors">
              <span className="text-[#e0e0e0] text-[13px] font-medium">{o}</span>
              {o === 'Last edited' && <Check className="w-4 h-4 text-[#a0a0a0]" />}
            </button>
          ))}
          <button className="flex items-center justify-between w-full px-4 py-2 text-left cursor-default">
            <span className="text-[#666] text-[13px] font-medium">Relevance</span>
            <Info className="w-4 h-4 text-[#666]" />
          </button>
          <div className="h-px bg-[#333] my-1.5" />
          <div className="px-4 py-2"><span className="text-[#888] text-[13px] font-medium">Order</span></div>
          {['Newest first','Oldest first'].map(o => (
            <button key={o} className="flex items-center justify-between w-full px-4 py-2 text-left hover:bg-white/5 transition-colors">
              <span className="text-[#e0e0e0] text-[13px] font-medium">{o}</span>
              {o === 'Newest first' && <Check className="w-4 h-4 text-[#a0a0a0]" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

const SimpleDropdown = ({ label, options }: { label: string; options: string[] }) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setIsOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);
  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setIsOpen(!isOpen)} className={`flex items-center gap-2 bg-transparent hover:bg-white/5 text-[#e0e0e0] px-3.5 py-1.5 rounded-lg text-[13px] font-medium transition-colors border ${isOpen ? 'border-[#555] bg-white/5' : 'border-white/20'}`}>
        {label} <ChevronDown className="w-4 h-4 text-[#a0a0a0] ml-1" />
      </button>
      {isOpen && (
        <div className="absolute top-full left-0 mt-1.5 w-[200px] bg-[#1a1a1a] border border-[#333] rounded-xl shadow-xl overflow-hidden z-50 py-1.5">
          {options.map((o, i) => (
            <button key={o} className="flex items-center justify-between w-full px-4 py-2 text-left hover:bg-white/5 transition-colors">
              <span className="text-[#e0e0e0] text-[13px] font-medium">{o}</span>
              {i === 0 && <Check className="w-4 h-4 text-[#a0a0a0]" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

const IconButton = ({ icon, active }: { icon: React.ReactElement; active?: boolean }) => (
  <button className={`p-2 rounded-[10px] transition-colors border ${active ? 'bg-[#f8f8f8] text-[#141414] border-[#f8f8f8]' : 'bg-transparent text-[#a0a0a0] border-white/20 hover:text-[#e0e0e0] hover:bg-white/5'}`}>
    {React.cloneElement(icon, { className: 'w-4 h-4' })}
  </button>
);

/* ─── Project Card ─── */
const ProjectCard = ({ id, title, edited, image, avatar, avatarColor, isStarred, onToggleStar, onRename }: any) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [editTitle, setEditTitle] = useState(title);
  const menuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => { if (menuRef.current && !menuRef.current.contains(e.target as Node)) setIsMenuOpen(false); };
    document.addEventListener('mousedown', h);
    return () => document.removeEventListener('mousedown', h);
  }, []);
  useEffect(() => { if (isRenaming && inputRef.current) { inputRef.current.focus(); inputRef.current.select(); } }, [isRenaming]);
  const submit = () => { if (editTitle.trim() && editTitle !== title) onRename(id, editTitle.trim()); else setEditTitle(title); setIsRenaming(false); };
  const onKey = (e: React.KeyboardEvent) => { if (e.key === 'Enter') submit(); else if (e.key === 'Escape') { setEditTitle(title); setIsRenaming(false); } };
  return (
    <div className="group cursor-pointer flex flex-col relative">
      <div className="aspect-video bg-transparent rounded-xl overflow-hidden mb-3 relative border border-white/10">
        <img src={image} alt={title} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
        <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={(e) => { e.stopPropagation(); onToggleStar(id); }} className="bg-[#222]/80 hover:bg-[#333] backdrop-blur-sm p-2 rounded-lg transition-colors">
            <Star className={`w-4 h-4 ${isStarred ? 'text-yellow-400 fill-yellow-400' : 'text-[#e0e0e0]'}`} />
          </button>
        </div>
      </div>
      <div className="flex items-start gap-3 relative">
        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-white text-[11px] font-medium shrink-0 ${avatarColor}`}>{avatar}</div>
        <div className="flex flex-col justify-center min-h-[28px] flex-1">
          {isRenaming ? (
            <input ref={inputRef} type="text" value={editTitle} onChange={(e) => setEditTitle(e.target.value)} onBlur={submit} onKeyDown={onKey} className="bg-[#141414] text-white font-medium text-[14px] leading-tight mb-1 border border-blue-500 rounded px-1 outline-none w-full" onClick={(e) => e.stopPropagation()} />
          ) : (
            <h3 className="text-[#e0e0e0] font-medium text-[14px] leading-tight mb-1 line-clamp-1 group-hover:text-blue-400 transition-colors">{title}</h3>
          )}
          <p className="text-[#a0a0a0] text-[12px] leading-tight">{edited}</p>
        </div>
        <div className={`flex items-center gap-1 transition-opacity self-center ${isMenuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
          <button className="p-1.5 text-[#a0a0a0] hover:text-[#e0e0e0] transition-colors rounded-md hover:bg-white/5"><Link2 className="w-4 h-4" /></button>
          <div className="relative" ref={menuRef}>
            <button onClick={(e) => { e.stopPropagation(); setIsMenuOpen(!isMenuOpen); }} className={`p-1.5 transition-colors rounded-md hover:bg-white/5 ${isMenuOpen ? 'text-[#e0e0e0] bg-white/5' : 'text-[#a0a0a0] hover:text-[#e0e0e0]'}`}>
              <MoreHorizontal className="w-4 h-4" />
            </button>
            {isMenuOpen && (
              <div className="absolute right-0 top-full mt-1 w-56 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-xl py-1.5 z-50">
                <button className="w-full flex items-center gap-3 px-3 py-2 text-[13px] text-white hover:bg-white/5 transition-colors"><ArrowUpRight className="w-4 h-4 text-[#a0a0a0]" />View published site</button>
                <button className="w-full flex items-center gap-3 px-3 py-2 text-[13px] text-white hover:bg-white/5 transition-colors"><BarChart2 className="w-4 h-4 text-[#a0a0a0]" />Analytics</button>
                <div className="h-px bg-white/10 my-1.5 mx-3" />
                <button onClick={(e) => { e.stopPropagation(); setIsMenuOpen(false); setIsRenaming(true); }} className="w-full flex items-center gap-3 px-3 py-2 text-[13px] text-white hover:bg-white/5 transition-colors"><Edit2 className="w-4 h-4 text-[#a0a0a0]" />Rename</button>
                <button className="w-full flex items-center gap-3 px-3 py-2 text-[13px] text-white hover:bg-white/5 transition-colors"><Settings className="w-4 h-4 text-[#a0a0a0]" />Settings</button>
                <div className="h-px bg-white/10 my-1.5 mx-3" />
                <button className="w-full flex items-center gap-3 px-3 py-2 text-[13px] text-white hover:bg-white/5 transition-colors"><Trash2 className="w-4 h-4 text-[#a0a0a0]" />Delete</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/* ─── Project List Item ─── */
const ProjectListItem = ({ id, title, edited, createdAt, creator, image, avatar, avatarColor, isStarred, onToggleStar }: any) => (
  <div className="group grid grid-cols-[116px_minmax(300px,2.5fr)_minmax(200px,1fr)_minmax(150px,1fr)_40px] gap-4 items-center px-3 py-1.5 hover:bg-white/5 transition-colors rounded-xl cursor-pointer">
    <div className="w-[116px] h-[65px] bg-[#141414] rounded-lg overflow-hidden shrink-0 border border-white/10">
      <img src={image} alt={title} className="w-full h-full object-cover" />
    </div>
    <div className="flex flex-col justify-center">
      <h3 className="text-[#e0e0e0] font-medium text-[14px] leading-tight mb-1 group-hover:text-blue-400 transition-colors">{title}</h3>
      <p className="text-[#a0a0a0] text-[12px] leading-tight">{edited}</p>
    </div>
    <div className="text-[#a0a0a0] text-[13px]">{createdAt}</div>
    <div className="flex items-center gap-2">
      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-medium shrink-0 ${avatarColor}`}>{avatar}</div>
      <span className="text-[#e0e0e0] text-[13px]">{creator}</span>
    </div>
    <div className="flex justify-end pr-2">
      <button onClick={(e) => { e.stopPropagation(); onToggleStar(id); }} className="focus:outline-none">
        <Star className={`w-4 h-4 transition-colors ${isStarred ? 'text-yellow-400 fill-yellow-400' : 'text-[#666] group-hover:text-[#a0a0a0]'}`} />
      </button>
    </div>
  </div>
);

/* ─── Main Page ─── */
export default function AllProjects() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [starredProjects, setStarredProjects] = useState<number[]>([]);
  const [activeProjects, setActiveProjects] = useState(initialActiveProjects);
  const [inactiveProjects, setInactiveProjects] = useState(initialInactiveProjects);

  const firstName = user?.firstName || user?.username || user?.emailAddresses?.[0]?.emailAddress?.split('@')[0] || 'there';
  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  const toggleStar = (id: number) => setStarredProjects(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  const handleRename = (id: number, newTitle: string) => {
    setActiveProjects(prev => prev.map(p => p.id === id ? { ...p, title: newTitle } : p));
    setInactiveProjects(prev => prev.map(p => p.id === id ? { ...p, title: newTitle } : p));
  };

  const filteredActive = activeProjects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase()));
  const filteredInactive = inactiveProjects.filter(p => p.title.toLowerCase().includes(searchQuery.toLowerCase()));

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

      {/* ── Sidebar ── */}
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
                    <SidebarItem icon={CustomGrid} label="All projects" active />
                    <SidebarItem icon={CustomStar} label="Starred" onClick={() => navigate('/starred')} />
                    <SidebarItem icon={CustomUser} label="Created by me" onClick={() => navigate('/created-by-me')} />
                    <SidebarItem icon={CustomUsers} label="Shared with me" onClick={() => navigate('/shared-with-me')} />
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
                <Tooltip text="All projects"><button className="bg-neutral-800/50 text-white w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomGrid size={14} /></button></Tooltip>
                <Tooltip text="Starred"><button onClick={() => navigate('/starred')} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomStar size={14} /></button></Tooltip>
                <Tooltip text="Created by me"><button onClick={() => navigate('/created-by-me')} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomUser size={14} /></button></Tooltip>
                <Tooltip text="Shared with me"><button onClick={() => navigate('/shared-with-me')} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomUsers size={14} /></button></Tooltip>
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

      {/* ── Main Content ── */}
      <div className="flex-1 relative flex flex-col overflow-hidden rounded-[32px] bg-[#0d0d0d] m-3 ml-2 border border-white/5 shadow-2xl">
        <div className="flex-1 overflow-y-auto p-6 md:p-8">
          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <h1 className="text-[22px] font-semibold tracking-tight">Projects</h1>
          </div>

          {/* Toolbar */}
          <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4 mb-10">
            <div className="relative flex-1 xl:mr-8">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#a0a0a0]" />
              <input type="text" placeholder="Search projects..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-transparent text-[#e0e0e0] rounded-lg pl-10 pr-4 py-1.5 text-[13px] border border-white/20 focus:border-white/40 focus:outline-none transition-colors placeholder:text-[#a0a0a0]" />
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <SortDropdown />
              <SimpleDropdown label="Any visibility" options={['Any visibility','Public','Workspace']} />
              <SimpleDropdown label="Any status" options={['Any status','All published','Internally published','Externally published','Not published']} />
              <SimpleDropdown label="All creators" options={['All creators','Think (You)']} />
              <div className="flex items-center gap-2 ml-2">
                <IconButton icon={<Layers />} active />
                <IconButton icon={<SquareDashed />} />
                <div className="flex items-center bg-[#222] rounded-[10px] p-1 ml-1">
                  <button onClick={() => setViewMode('grid')} className={`p-1.5 rounded-md transition-colors ${viewMode === 'grid' ? 'bg-[#141414] text-[#e0e0e0] shadow-sm' : 'text-[#a0a0a0] hover:text-[#e0e0e0]'}`}><LayoutGrid className="w-4 h-4" /></button>
                  <button onClick={() => setViewMode('list')} className={`p-1.5 rounded-md transition-colors ${viewMode === 'list' ? 'bg-[#141414] text-[#e0e0e0] shadow-sm' : 'text-[#a0a0a0] hover:text-[#e0e0e0]'}`}><List className="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          </div>

          {filteredActive.length === 0 && filteredInactive.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center py-24 select-none">
              <div className="mb-10 relative w-[200px] h-[140px]" style={{ perspective: '800px' }}>
                <div className="absolute inset-0 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02]"
                  style={{ transform: 'rotateY(-15deg) rotateX(8deg)', boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)' }}>
                  <div className="p-4 flex flex-col gap-2.5">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-md bg-white/10 border border-white/10" />
                      <div className="h-2 w-20 rounded-full bg-white/10" />
                    </div>
                    <div className="h-[60px] rounded-xl bg-white/5 border border-white/5" />
                    <div className="flex gap-1.5">
                      <div className="h-1.5 w-12 rounded-full bg-white/10" />
                      <div className="h-1.5 w-8 rounded-full bg-white/[0.06]" />
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 rounded-2xl border border-white/5 bg-white/[0.015]"
                  style={{ transform: 'rotateY(-15deg) rotateX(8deg) translateZ(-24px) translateX(12px) translateY(8px)' }} />
              </div>
              <h2 className="text-[#f4f4f5] text-[24px] font-semibold text-center leading-[1.3] tracking-tight mb-3">
                No projects match your search
              </h2>
              <p className="text-[#71717a] text-[14px] text-center mb-8">
                Try a different search term or clear the filter.
              </p>
              <button
                onClick={() => setSearchQuery('')}
                className="px-4 py-2 bg-transparent border border-[#3f3f46] rounded-lg text-sm font-medium text-[#e4e4e7] hover:bg-[#27272a] hover:text-white transition-all duration-200 shadow-sm"
              >
                Clear search
              </button>
            </div>
          ) : viewMode === 'grid' ? (
            <>
              <div className="mb-12">
                <h2 className="text-[13px] font-semibold text-[#a0a0a0] mb-4 tracking-wide">Active in last 14 days</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-10">
                  <div className="group cursor-pointer flex flex-col">
                    <div className="aspect-video bg-transparent border-2 border-dashed border-white/20 rounded-xl flex items-center justify-center group-hover:border-white/40 transition-colors mb-3">
                      <Plus className="w-6 h-6 text-[#666] group-hover:text-[#888] transition-colors" />
                    </div>
                    <h3 className="text-[#e0e0e0] font-medium text-[14px] px-1">Create new project</h3>
                  </div>
                  {filteredActive.map(p => <ProjectCard key={p.id} {...p} isStarred={starredProjects.includes(p.id)} onToggleStar={toggleStar} onRename={handleRename} />)}
                </div>
              </div>
              {filteredInactive.length > 0 && (
                <div>
                  <h2 className="text-[13px] font-semibold text-[#a0a0a0] mb-4 tracking-wide">Inactive 60+ days</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-10">
                    {filteredInactive.map(p => <ProjectCard key={p.id} {...p} isStarred={starredProjects.includes(p.id)} onToggleStar={toggleStar} onRename={handleRename} />)}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col w-full">
              <div className="grid grid-cols-[116px_minmax(300px,2.5fr)_minmax(200px,1fr)_minmax(150px,1fr)_40px] gap-4 px-3 mb-6 text-[13px] font-medium text-[#a0a0a0]">
                <div /><div>Name</div><div>Created at</div><div>Created by</div><div />
              </div>
              <div className="mb-8">
                <h2 className="text-[13px] font-semibold text-[#e0e0e0] mb-4 px-3 tracking-wide">Active in last 14 days</h2>
                <div className="flex flex-col gap-2">
                  {filteredActive.map(p => <ProjectListItem key={p.id} {...p} isStarred={starredProjects.includes(p.id)} onToggleStar={toggleStar} onRename={handleRename} />)}
                </div>
              </div>
              {filteredInactive.length > 0 && (
                <div>
                  <h2 className="text-[13px] font-semibold text-[#e0e0e0] mb-4 px-3 tracking-wide">Inactive 60+ days</h2>
                  <div className="flex flex-col gap-2">
                    {filteredInactive.map(p => <ProjectListItem key={p.id} {...p} isStarred={starredProjects.includes(p.id)} onToggleStar={toggleStar} onRename={handleRename} />)}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
