import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import { useAuth, useUser, useClerk } from '@clerk/clerk-react';
import {
  ChevronDown, Gift, Zap, LogOut, Map, Mic, ArrowUp,
  Plus, X, Check, FileCode2, ChevronRight, Loader2,
  CheckCircle, AlertCircle, Send, Star,
} from 'lucide-react';
import { makeApi, type Project, type SseProgressEvent, type GeneratedFile } from '../lib/api';
import { SearchModal } from '../components/SearchModal';
// @ts-ignore
import bgImage from '../background.png.png';
// @ts-ignore
import logo from '../logo.png';

/* ─── Sidebar SVG Icons ─── */
const CustomHome = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M3 10l9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><line x1="9" y1="16" x2="15" y2="16" /></svg>
);
const CustomSearch = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
);
const CustomCompass = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="12" cy="12" r="10" /><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" /></svg>
);
const CustomGrid = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="7" cy="7" r="3" /><circle cx="17" cy="7" r="3" /><circle cx="7" cy="17" r="3" /><circle cx="17" cy="17" r="3" /></svg>
);
const CustomStar = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
);
const CustomUser = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
);
const CustomUsers = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
);
const CustomPanelLeft = ({ size = 16, className = '' }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="18" height="18" x="3" y="3" rx="2" /><path d="M9 3v18" /></svg>
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

const SidebarItem = ({ icon: Icon, label, active = false, badge = null, onClick }: any) => (
  <button onClick={onClick} className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-[13px] transition-colors ${active ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-neutral-800/30'}`}>
    <div className="flex items-center gap-3">
      {Icon && <Icon size={14} className="text-white" />}
      <span className="font-normal">{label}</span>
    </div>
    {badge && <span className="text-[9px] font-semibold bg-neutral-800 text-white px-1.5 py-0.5 rounded border border-neutral-700">{badge}</span>}
  </button>
);

const ProjectItem = ({ label, active, onClick }: { label: string; active?: boolean; onClick?: () => void }) => (
  <button onClick={onClick} className={`w-full flex items-center gap-3 px-3 py-1.5 rounded-lg text-[13px] transition-colors ${active ? 'bg-neutral-800/50 text-white' : 'text-white hover:bg-neutral-800/30'}`}>
    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white flex-shrink-0">
      <polygon points="12 2 22 12 12 22 2 12 12 2" />
    </svg>
    <span className="truncate font-normal">{label}</span>
  </button>
);

/* ─── Types ─── */
type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: 'running' | 'done' | 'error';
  progress?: number;
  step?: string;
  fileCount?: number;
};

/* ─── Code viewer ─── */
function CodePanel({ files }: { files: GeneratedFile[] }) {
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    if (files.length > 0 && !selected) setSelected(files[0].file_path);
  }, [files]);

  const selectedFile = files.find(f => f.file_path === selected);

  if (files.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 text-[#555]">
        <FileCode2 className="w-10 h-10" />
        <p className="text-[14px]">No files generated yet</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex min-h-0 overflow-hidden">
      {/* File list */}
      <div className="w-56 flex-shrink-0 border-r border-white/5 overflow-y-auto bg-[#0a0a0a] py-2">
        {files.map(f => {
          const parts = f.file_path.split('/');
          const name = parts[parts.length - 1];
          const dir = parts.length > 1 ? parts.slice(0, -1).join('/') + '/' : '';
          return (
            <button
              key={f.id}
              onClick={() => setSelected(f.file_path)}
              className={`w-full flex items-start gap-2 px-3 py-1.5 text-left transition-colors ${selected === f.file_path ? 'bg-white/10 text-white' : 'text-[#888] hover:text-white hover:bg-white/5'}`}
            >
              <FileCode2 className="w-3 h-3 flex-shrink-0 mt-0.5" />
              <div className="min-w-0">
                {dir && <div className="text-[10px] text-[#555] truncate">{dir}</div>}
                <div className="text-[12px] truncate">{name}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Code content */}
      <div className="flex-1 overflow-auto bg-[#050505]">
        {selectedFile ? (
          <div className="p-5">
            <div className="text-[11px] text-[#555] mb-3 font-mono border-b border-white/5 pb-2">{selectedFile.file_path}</div>
            <pre className="text-[13px] text-[#ccc] font-mono whitespace-pre-wrap leading-relaxed">
              {selectedFile.content}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-[#555] text-[13px]">
            Select a file to view
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main page ─── */
export default function ProjectView() {
  const { id: projectId } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const { user } = useUser();
  const { signOut } = useClerk();

  /* sidebar */
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [recentProjects, setRecentProjects] = useState<Project[]>([]);

  /* project state */
  const [project, setProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<GeneratedFile[]>([]);
  const [isLoadingProject, setIsLoadingProject] = useState(true);
  const [activeTab, setActiveTab] = useState<'code' | 'preview'>('code');

  /* chat */
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  /* prompt input */
  const [promptValue, setPromptValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const cleanupRef = useRef<(() => void) | null>(null);

  const firstName = user?.firstName || user?.username || user?.emailAddresses?.[0]?.emailAddress?.split('@')[0] || 'there';
  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  /* scroll chat to bottom */
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /* keyboard shortcuts */
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setIsSearchOpen(true); }
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') { e.preventDefault(); setIsSidebarOpen(p => !p); }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, []);

  /* load project + files + recent projects */
  useEffect(() => {
    if (!projectId) return;
    const api = makeApi(() => getToken());

    Promise.all([
      api.projects.list(),
      api.files.forProject(projectId),
    ]).then(([allProjects, fileList]) => {
      const proj = allProjects.find(p => p.id === projectId) ?? null;
      setProject(proj);
      setFiles(fileList);
      setRecentProjects(allProjects.slice(0, 8));
    }).catch(() => {}).finally(() => setIsLoadingProject(false));

    /* seed chat with the initial prompt from URL if present */
    const initialPrompt = searchParams.get('prompt');
    const jobId = searchParams.get('job_id');

    if (initialPrompt) {
      const userMsgId = crypto.randomUUID();
      const asstMsgId = crypto.randomUUID();
      setMessages([
        { id: userMsgId, role: 'user', content: initialPrompt },
        { id: asstMsgId, role: 'assistant', content: '', status: 'running', progress: 0 },
      ]);

      if (jobId) {
        startStreaming(projectId, jobId, asstMsgId, api);
      }
    }

    return () => { cleanupRef.current?.(); };
  }, [projectId]);

  function startStreaming(pid: string, jobId: string, asstMsgId: string, api: ReturnType<typeof makeApi>) {
    if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
    const cleanup = api.streamJob(pid, jobId, (event: SseProgressEvent) => {
      if (event.type === 'progress') {
        setMessages(prev => prev.map(m =>
          m.id === asstMsgId ? { ...m, progress: event.progress ?? 0, step: event.current_step ?? undefined } : m
        ));
      } else if (event.type === 'done') {
        setMessages(prev => prev.map(m =>
          m.id === asstMsgId ? { ...m, status: 'done', progress: 100 } : m
        ));
        const innerApi = makeApi(() => getToken());
        innerApi.files.forProject(pid).then(setFiles).catch(() => {});
        if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
      } else if (event.type === 'error') {
        setMessages(prev => prev.map(m =>
          m.id === asstMsgId ? { ...m, status: 'error', content: event.error ?? 'Generation failed' } : m
        ));
        if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
      }
    }, getToken);
    cleanupRef.current = cleanup;
  }

  const handleSubmit = async () => {
    const text = promptValue.trim();
    if (!text || isSubmitting || !projectId) return;
    setIsSubmitting(true);
    setSubmitError('');
    setPromptValue('');

    const userMsgId = crypto.randomUUID();
    const asstMsgId = crypto.randomUUID();
    setMessages(prev => [
      ...prev,
      { id: userMsgId, role: 'user', content: text },
      { id: asstMsgId, role: 'assistant', content: '', status: 'running', progress: 0 },
    ]);

    try {
      const api = makeApi(() => getToken());
      const gen = await api.generate({ project_id: projectId, prompt: text, mode: 'autonomous' });
      startStreaming(projectId, gen.job_id, asstMsgId, api);
    } catch (err: any) {
      setMessages(prev => prev.map(m =>
        m.id === asstMsgId ? { ...m, status: 'error', content: err.message || 'Something went wrong' } : m
      ));
      setSubmitError(err.message || 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  if (isLoadingProject) {
    return <div className="min-h-screen bg-[#171717] flex items-center justify-center"><div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" /></div>;
  }

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
                    <SidebarItem icon={CustomGrid} label="All projects" onClick={() => navigate('/all-projects')} />
                    <SidebarItem icon={CustomStar} label="Starred" onClick={() => navigate('/starred')} />
                    <SidebarItem icon={CustomUser} label="Created by me" onClick={() => navigate('/created-by-me')} />
                    <SidebarItem icon={CustomUsers} label="Shared with me" onClick={() => navigate('/shared-with-me')} />
                  </div>
                  {recentProjects.length > 0 && (
                    <div className="flex flex-col gap-0.5">
                      <div className="px-3 py-2 text-[13px] font-semibold text-[#a3a3a3]">Recents</div>
                      {recentProjects.map(p => (
                        <ProjectItem key={p.id} label={p.name} active={p.id === projectId} onClick={() => navigate(`/projects/${p.id}`)} />
                      ))}
                    </div>
                  )}
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
                <Tooltip text="All projects"><button onClick={() => navigate('/all-projects')} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomGrid size={14} /></button></Tooltip>
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

      {/* ── Main content area ── */}
      <div className="flex-1 flex overflow-hidden rounded-[32px] bg-[#0d0d0d] m-3 ml-2 border border-white/5 shadow-2xl">

        {/* ── Left: Chat panel ── */}
        <div className="w-[360px] flex-shrink-0 flex flex-col border-r border-white/5 bg-[#0d0d0d]">
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-white/5">
            <button onClick={() => navigate('/dashboard')} className="text-[#888] hover:text-white transition-colors flex-shrink-0">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            </button>
            <div className="flex-1 min-w-0">
              <h1 className="text-[14px] font-semibold truncate text-white">{project?.name ?? 'Loading…'}</h1>
              {project && (
                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
                  project.mode === 'max' ? 'text-orange-300' :
                  project.mode === 'autonomous' ? 'text-purple-300' : 'text-blue-300'
                }`}>{project.mode}</span>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4">
            {messages.length === 0 && (
              <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center py-16">
                <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                  <img src={logo} alt="Logo" className="w-5 h-5 object-contain rounded" />
                </div>
                <p className="text-[#555] text-[13px]">Describe what you want to build</p>
              </div>
            )}

            {messages.map(msg => (
              <div key={msg.id} className={`flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                {msg.role === 'user' ? (
                  <div className="max-w-[85%] bg-[#1c1c1c] border border-white/10 rounded-2xl rounded-tr-sm px-4 py-2.5">
                    <p className="text-[14px] text-[#e0e0e0] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  </div>
                ) : (
                  <div className="w-full">
                    {msg.status === 'running' && (
                      <div className="bg-[#111] border border-white/5 rounded-2xl rounded-tl-sm px-4 py-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin flex-shrink-0" />
                          <span className="text-[13px] text-blue-300 truncate">{msg.step || 'Generating…'}</span>
                          <span className="text-[11px] text-blue-400 ml-auto flex-shrink-0">{msg.progress ?? 0}%</span>
                        </div>
                        <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${msg.progress ?? 0}%` }} />
                        </div>
                      </div>
                    )}
                    {msg.status === 'done' && (
                      <div className="bg-[#111] border border-white/5 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                        <span className="text-[13px] text-green-300">
                          Done — {files.length} file{files.length !== 1 ? 's' : ''} generated
                        </span>
                      </div>
                    )}
                    {msg.status === 'error' && (
                      <div className="bg-[#111] border border-red-500/20 rounded-2xl rounded-tl-sm px-4 py-3 flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                        <span className="text-[13px] text-red-300 leading-relaxed">{msg.content || 'Generation failed'}</span>
                      </div>
                    )}
                    {!msg.status && msg.content && (
                      <div className="bg-[#111] border border-white/5 rounded-2xl rounded-tl-sm px-4 py-3">
                        <p className="text-[14px] text-[#e0e0e0] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Prompt input */}
          <div className="p-3 border-t border-white/5">
            {submitError && <p className="text-red-400 text-[12px] mb-2 px-1">{submitError}</p>}
            <div className="relative bg-[#161616] border border-white/10 rounded-2xl px-4 py-3 focus-within:border-white/25 transition-colors">
              <textarea
                value={promptValue}
                onChange={e => setPromptValue(e.target.value)}
                onKeyDown={onKey}
                placeholder="Ask Thinksoft to..."
                rows={1}
                disabled={isSubmitting}
                className="w-full bg-transparent text-[14px] text-white placeholder:text-[#555] resize-none outline-none leading-relaxed max-h-32 overflow-y-auto disabled:opacity-50"
                style={{ fieldSizing: 'content' } as React.CSSProperties}
              />
              <div className="flex items-center justify-between mt-2">
                <button className="text-[#555] hover:text-[#888] transition-colors">
                  <Plus size={18} strokeWidth={1.75} />
                </button>
                <div className="flex items-center gap-2">
                  <button className="text-[#555] hover:text-[#888] transition-colors">
                    <Map size={15} strokeWidth={1.75} />
                  </button>
                  <button className="text-[#555] hover:text-[#888] transition-colors">
                    <Mic size={15} strokeWidth={1.75} />
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={!promptValue.trim() || isSubmitting}
                    className={`w-7 h-7 rounded-full flex items-center justify-center transition-colors ml-1 ${promptValue.trim() && !isSubmitting ? 'bg-white text-black hover:bg-gray-200' : 'bg-[#333] text-[#666]'}`}
                  >
                    {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ArrowUp size={14} strokeWidth={2} />}
                  </button>
                </div>
              </div>
            </div>
            <p className="text-[#444] text-[11px] mt-1.5 px-1">Enter to send · Shift+Enter for new line</p>
          </div>
        </div>

        {/* ── Right: Code panel ── */}
        <div className="flex-1 flex flex-col min-w-0 bg-[#050505]">
          {/* Tab bar */}
          <div className="flex items-center border-b border-white/5 px-4 gap-1 flex-shrink-0">
            {(['code', 'preview'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-3 text-[13px] font-medium transition-colors capitalize border-b-2 ${activeTab === tab ? 'text-white border-white' : 'text-[#666] border-transparent hover:text-[#aaa]'}`}
              >
                {tab}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-2 py-2">
              {files.length > 0 && (
                <span className="text-[11px] text-[#555]">{files.length} file{files.length !== 1 ? 's' : ''}</span>
              )}
            </div>
          </div>

          {/* Tab content */}
          {activeTab === 'code' ? (
            <CodePanel files={files} />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center gap-3 text-[#555]">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="opacity-50"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              <p className="text-[13px]">Preview coming soon</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
