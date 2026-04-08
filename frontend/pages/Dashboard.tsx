import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useUser, useClerk } from '@clerk/clerk-react';
import {
  ChevronDown,
  Gift,
  Zap,
  Plus,
  Map,
  Mic,
  ArrowUp,
  Inbox,
  X,
  Check,
  LogOut,
} from 'lucide-react';
import { SearchModal } from '../components/SearchModal';
// @ts-ignore
import bgImage from '../background.png.png';
// @ts-ignore
import logo from '../logo.png';

const Tooltip = ({ children, text, shortcut, position = 'right' }: { children: React.ReactNode; text: string; shortcut?: string; position?: 'right' | 'top' }) => (
  <div className="relative group/tooltip flex items-center justify-center">
    {children}
    <div className={`absolute ${position === 'right' ? 'left-full ml-3 top-1/2 -translate-y-1/2 translate-x-[-4px] group-hover/tooltip:translate-x-0' : 'bottom-full mb-3 left-1/2 -translate-x-1/2 translate-y-[4px] group-hover/tooltip:translate-y-0'} px-3 py-2 bg-[#1e1e1e] text-[#eeeeee] text-[13px] font-medium rounded-xl opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all duration-200 delay-150 ease-out pointer-events-none whitespace-nowrap z-[200] flex items-center gap-2`}>
      {text}
      {shortcut && (
        <span className="bg-[#333] px-1.5 py-0.5 rounded-md text-[11px] text-neutral-300 font-semibold tracking-wide">
          {shortcut}
        </span>
      )}
    </div>
  </div>
);

const VoiceVisualizer = ({ volume }: { volume: number }) => (
  <div className="w-full flex items-center justify-center gap-[4px] overflow-hidden px-4">
    {[...Array(90)].map((_, i) => {
      const distance = Math.abs(i - 45) / 45;
      const maxBarHeight = 24 * (1 - distance);
      const activeHeight = 4 + volume * maxBarHeight * (0.5 + Math.random() * 0.5);
      return (
        <motion.div
          key={i}
          className="w-[3px] bg-neutral-400 rounded-full"
          animate={{ height: volume > 0.01 ? activeHeight : 4 }}
          transition={{ duration: 0.1 }}
        />
      );
    })}
  </div>
);

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

const PHRASES = [
  'make a document that...',
  'create a blog about...',
  'build a prototype...',
  'build a landing page for my...',
  'create a presentation...',
];

export default function Dashboard() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [promptValue, setPromptValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [tempVoicePrompt, setTempVoicePrompt] = useState('');
  const [voiceError, setVoiceError] = useState('');
  const [volume, setVolume] = useState(0);

  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const firstName = user?.firstName || user?.username || user?.emailAddresses?.[0]?.emailAddress?.split('@')[0] || 'there';
  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  const startAudioMeter = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    audioContextRef.current = audioContext;
    analyserRef.current = analyser;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const updateVolume = () => {
      if (!analyserRef.current) return;
      analyserRef.current.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
      setVolume(Math.min(1, sum / dataArray.length / 128));
      animationFrameRef.current = requestAnimationFrame(updateVolume);
    };
    updateVolume();
  };

  const stopAudioMeter = () => {
    if (animationFrameRef.current) { cancelAnimationFrame(animationFrameRef.current); animationFrameRef.current = null; }
    if (audioContextRef.current) { audioContextRef.current.close(); audioContextRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach(t => t.stop()); streamRef.current = null; }
    setVolume(0);
  };

  const startListening = async () => {
    setVoiceError('');
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError('Speech recognition not supported in this browser.');
      setIsListening(true);
      return;
    }
    setIsListening(true);
    try {
      await startAudioMeter();
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.onstart = () => { setTempVoicePrompt(''); setVoiceError(''); };
      let finalTranscript = '';
      recognition.onresult = (event: any) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) { finalTranscript += event.results[i][0].transcript; setTempVoicePrompt(finalTranscript); }
          else { interim += event.results[i][0].transcript; setTempVoicePrompt(finalTranscript + interim); }
        }
      };
      recognition.onerror = (event: any) => {
        if (event.error === 'not-allowed') setVoiceError('Microphone access denied. Please allow it in your browser settings.');
        else setVoiceError(`Error: ${event.error}`);
      };
      recognition.start();
      recognitionRef.current = recognition;
    } catch {
      setVoiceError('Microphone access denied. Please allow it in your browser settings.');
    }
  };

  const cancelListening = () => {
    recognitionRef.current?.stop();
    stopAudioMeter();
    setIsListening(false);
    setTempVoicePrompt('');
  };

  const acceptListening = () => {
    recognitionRef.current?.stop();
    stopAudioMeter();
    setIsListening(false);
    setIsTranscribing(true);
    setTimeout(() => {
      if (tempVoicePrompt.trim()) setPromptValue(prev => prev + (prev && tempVoicePrompt ? ' ' : '') + tempVoicePrompt);
      setTempVoicePrompt('');
      setIsTranscribing(false);
    }, 1500);
  };

  useEffect(() => {
    const typingSpeed = 25;
    const deletingSpeed = 15;
    const pauseDuration = 1500;
    const handleTyping = () => {
      const phrase = PHRASES[currentPhraseIndex];
      if (!isDeleting) {
        setCurrentText(phrase.substring(0, currentText.length + 1));
        if (currentText === phrase) setTimeout(() => setIsDeleting(true), pauseDuration);
      } else {
        setCurrentText(phrase.substring(0, currentText.length - 1));
        if (currentText === '') { setIsDeleting(false); setCurrentPhraseIndex(prev => (prev + 1) % PHRASES.length); }
      }
    };
    const timer = setTimeout(handleTyping, isDeleting ? deletingSpeed : currentText === PHRASES[currentPhraseIndex] ? pauseDuration : typingSpeed);
    return () => clearTimeout(timer);
  }, [currentText, isDeleting, currentPhraseIndex]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); setIsSearchOpen(true); }
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') { e.preventDefault(); setIsSidebarOpen(prev => !prev); }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-[#171717] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
      </div>
    );
  }
  if (!isSignedIn) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen bg-[#171717] text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: isSidebarOpen ? 240 : 64 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="flex-shrink-0 relative z-50 h-full bg-[#171717]"
      >
        <AnimatePresence initial={false}>
          {isSidebarOpen ? (
            <motion.div
              key="open"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 w-full overflow-hidden"
            >
              <div className="w-[240px] flex flex-col h-full">
                {/* Top */}
                <div className="p-4 flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <img src={logo} alt="Logo" className="w-6 h-6 object-contain rounded-md" />
                    <button onClick={() => setIsSidebarOpen(false)} className="text-white transition-colors cursor-ew-resize">
                      <CustomPanelLeft size={18} />
                    </button>
                  </div>
                  <button className="flex items-center justify-between w-full px-3 py-2 bg-neutral-800/40 hover:bg-neutral-800/60 rounded-lg border border-neutral-700/50 transition-colors">
                    <div className="flex items-center gap-2">
                      {user?.imageUrl ? (
                        <img src={user.imageUrl} alt="Avatar" className="w-5 h-5 rounded object-cover" />
                      ) : (
                        <div className="w-5 h-5 rounded bg-orange-600 flex items-center justify-center text-[11px] font-bold text-white">{initials}</div>
                      )}
                      <span className="text-[13px] font-semibold text-white truncate max-w-[120px]">{firstName}'s Thinksoft</span>
                    </div>
                    <ChevronDown size={14} className="text-white" />
                  </button>
                </div>

                {/* Scrollable */}
                <div className="flex-1 overflow-y-auto hide-scrollbar px-2 pb-4 flex flex-col gap-6">
                  <div className="flex flex-col gap-0.5">
                    <SidebarItem icon={CustomHome} label="Home" active />
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
                  <div className="flex flex-col gap-0.5">
                    <div className="px-3 py-2 text-[13px] font-semibold text-[#a3a3a3]">Recents</div>
                    {['Vibe Clone Studio', 'Landing Page Spark', 'SchoolDash Premium', 'Stream Central (82)', 'Stream Scene', 'Shop & Sign', 'Image Weaver', 'AI Launchpad'].map(n => <ProjectItem key={n} label={n} />)}
                  </div>
                </div>

                {/* Bottom */}
                <div className="p-4 flex flex-col gap-2 border-t border-neutral-800/50">
                  <button className="flex items-center justify-between w-full p-3 bg-[#1c1c1c] hover:bg-[#252525] rounded-xl border border-white/5 transition-colors">
                    <div className="flex flex-col items-start gap-0.5">
                      <span className="text-[13px] font-semibold text-white">Share Thinksoft</span>
                      <span className="text-[11px] text-white">100 credits per paid referral</span>
                    </div>
                    <div className="w-7 h-7 rounded-full border border-white/10 flex items-center justify-center text-white">
                      <Gift size={12} />
                    </div>
                  </button>
                  <button className="flex items-center justify-between w-full p-3 bg-[#1c1c1c] hover:bg-[#252525] rounded-xl border border-white/5 transition-colors mt-1">
                    <div className="flex flex-col items-start gap-0.5">
                      <span className="text-[13px] font-semibold text-white">Upgrade to Pro</span>
                      <span className="text-[11px] text-white">Unlock more features</span>
                    </div>
                    <div className="w-7 h-7 rounded-full bg-[#2b2d42] flex items-center justify-center text-white">
                      <Zap size={12} className="fill-white" />
                    </div>
                  </button>
                  <div className="flex items-center justify-between mt-4 px-1">
                    {user?.imageUrl ? (
                      <img src={user.imageUrl} alt="Avatar" className="w-6 h-6 rounded-full object-cover" />
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-[#5c9c49] flex items-center justify-center text-xs font-bold text-white">{initials}</div>
                    )}
                    <button onClick={() => signOut({ redirectUrl: '/' })} className="text-white transition-colors hover:text-red-400">
                      <LogOut size={18} strokeWidth={1.5} />
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="closed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 w-[64px] flex flex-col items-center py-5"
            >
              <Tooltip text="Open sidebar" shortcut="Ctrl B">
                <button onClick={() => setIsSidebarOpen(true)} className="text-white mb-6 hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors cursor-ew-resize">
                  <CustomPanelLeft size={16} />
                </button>
              </Tooltip>

              <div className="w-6 h-6 rounded-[5px] overflow-hidden mb-8 shadow-sm">
                <img src={logo} alt="Logo" className="w-full h-full object-cover" />
              </div>

              <div className="flex flex-col gap-2 w-full items-center">
                <Tooltip text="Home"><button className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors"><CustomHome size={14} /></button></Tooltip>
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
                {user?.imageUrl ? (
                  <img src={user.imageUrl} alt="Avatar" className="w-7 h-7 rounded-full object-cover cursor-pointer hover:opacity-90" />
                ) : (
                  <div className="w-7 h-7 rounded-full bg-[#5c9c49] flex items-center justify-center text-[13px] font-bold text-white cursor-pointer hover:opacity-90">{initials}</div>
                )}
                <Tooltip text="Sign out">
                  <button onClick={() => signOut({ redirectUrl: '/' })} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-xl transition-colors hover:text-red-400">
                    <LogOut size={16} strokeWidth={1.5} />
                  </button>
                </Tooltip>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 relative flex flex-col overflow-hidden rounded-[32px] bg-[#050505] m-3 ml-2 border border-white/5 shadow-2xl">
        {/* Background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none bg-[#050505] z-0">
          <div className="absolute top-0 inset-x-0 h-64 bg-gradient-to-b from-[#0a0a0a] to-transparent z-10" />
          <img
            src={bgImage}
            alt="Background"
            className="absolute inset-0 w-full h-full object-cover object-bottom opacity-100 -translate-y-12 scale-125"
          />
        </div>

        {/* Center Content */}
        <div className="flex-1 flex flex-col items-center justify-center z-10 px-4">
          <h1 className="text-[32px] font-semibold text-white mb-6 tracking-[-0.02em]" style={{ textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
            What's on your mind, {firstName}?
          </h1>

          {/* Prompt bar */}
          <div className="relative w-full max-w-[660px] group">
            {/* Animated gradient border */}
            <div className="absolute -inset-[1.5px] rounded-[34px] bg-[linear-gradient(to_right,#2b529f,#5e6eea,#b771f6,#f86ce0,#ff3b9a)] opacity-0 group-focus-within:opacity-100 [clip-path:inset(0_100%_0_0)] group-focus-within:[clip-path:inset(0_0_0_0)] transition-all duration-[1200ms] ease-[cubic-bezier(0.65,0,0.05,1)] pointer-events-none" />

            <div className="relative w-full h-[136px] bg-[#1c1c1c] rounded-[32px] p-4 shadow-2xl flex flex-col justify-between">
              {isListening ? (
                <div className="w-full h-full flex flex-col justify-between">
                  <div className="flex-1 flex flex-col items-center justify-center w-full overflow-hidden px-2 gap-3">
                    {voiceError ? (
                      <div className="text-red-400 text-[14px] text-center">{voiceError}</div>
                    ) : tempVoicePrompt ? (
                      <div className="text-white text-[15px] w-full text-center line-clamp-2 break-words">{tempVoicePrompt}</div>
                    ) : (
                      <VoiceVisualizer volume={volume} />
                    )}
                  </div>
                  <div className="flex items-center justify-between px-2 mb-1">
                    <button className="text-white hover:text-neutral-200 transition-colors"><Plus size={22} strokeWidth={1.5} /></button>
                    <div className="flex items-center gap-4">
                      <button onClick={cancelListening} className="text-neutral-400 hover:text-white transition-colors"><X size={18} strokeWidth={2} /></button>
                      <button onClick={acceptListening} className="bg-white text-black hover:bg-neutral-200 w-8 h-8 flex items-center justify-center rounded-full transition-colors ml-1"><Check size={16} strokeWidth={2.5} /></button>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {isTranscribing ? (
                    <div className="w-full h-full flex items-center">
                      <div className="text-neutral-400 font-normal text-[15px] px-2 animate-pulse">Transcribing...</div>
                    </div>
                  ) : (
                    <>
                      <input
                        type="text"
                        value={promptValue}
                        onChange={e => setPromptValue(e.target.value)}
                        placeholder={`Ask Thinksoft to ${currentText}`}
                        className="w-full bg-transparent text-neutral-200 placeholder-[#b0b0b0] font-normal outline-none text-[15px] px-2 mt-1"
                      />
                      <div className="flex items-center justify-between px-2 mb-1">
                        <button className="text-white hover:text-neutral-200 transition-colors"><Plus size={22} strokeWidth={1.5} /></button>
                        <div className="flex items-center gap-2">
                          <Tooltip text="Enable plan mode" shortcut="Alt P" position="top">
                            <button className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-full transition-colors">
                              <Map size={16} strokeWidth={1.75} />
                            </button>
                          </Tooltip>
                          <Tooltip text="Enable voice mode" shortcut="Alt V" position="top">
                            <button onClick={startListening} className="text-white hover:bg-[#333333] w-9 h-9 flex items-center justify-center rounded-full transition-colors">
                              <Mic size={16} strokeWidth={1.75} />
                            </button>
                          </Tooltip>
                          <button className={`${promptValue.trim().length > 0 ? 'bg-white text-black hover:bg-neutral-200' : 'bg-[#737373] text-[#1a1a1a] hover:bg-[#888888]'} w-9 h-9 flex items-center justify-center rounded-full transition-colors ml-1`}>
                            <ArrowUp size={18} strokeWidth={2} />
                          </button>
                        </div>
                      </div>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </div>
  );
}
