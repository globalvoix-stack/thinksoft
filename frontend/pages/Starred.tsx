import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Star } from 'lucide-react';
import { makeApi, type Project } from '../lib/api';
import ProjectsLayout from './ProjectsLayout';

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function Starred() {
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const { user } = useUser();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  useEffect(() => {
    const api = makeApi(() => getToken());
    api.projects.list()
      .then(data => setProjects(data.filter(p => p.is_starred)))
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  const toggleStar = async (id: string) => {
    const api = makeApi(() => getToken());
    try {
      const updated = await api.projects.toggleStar(id);
      if (!updated.is_starred) {
        setProjects(prev => prev.filter(p => p.id !== id));
      } else {
        setProjects(prev => prev.map(p => p.id === id ? { ...p, is_starred: true } : p));
      }
    } catch { /* ignore */ }
  };

  if (isLoading) {
    return (
      <ProjectsLayout activePage="starred">
        <div className="flex-1 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
        </div>
      </ProjectsLayout>
    );
  }

  if (projects.length === 0) {
    return (
      <ProjectsLayout activePage="starred">
        <div className="flex-1 flex flex-col items-center justify-center p-6 select-none">
          <div className="mb-10 relative w-[200px] h-[140px]" style={{ perspective: '800px' }}>
            <div className="absolute inset-0 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02]"
              style={{ transform: 'rotateY(-15deg) rotateX(8deg)', boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)' }}>
              <div className="p-4 flex flex-col gap-2.5">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-gradient-to-br from-yellow-400/30 to-orange-500/20 border border-yellow-400/20 flex items-center justify-center">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="text-yellow-400">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                  </div>
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
          <h1 className="text-[#f4f4f5] text-[26px] md:text-[30px] font-semibold text-center leading-[1.3] tracking-tight mb-3">
            Star projects to access<br />
            them quickly from any<br />
            workspace
          </h1>
          <p className="text-[#71717a] text-[14px] text-center mb-8">Your starred projects will show up here.</p>
          <button onClick={() => navigate('/all-projects')} className="px-4 py-2 bg-transparent border border-[#3f3f46] rounded-lg text-sm font-medium text-[#e4e4e7] hover:bg-[#27272a] hover:text-white transition-all duration-200 shadow-sm">
            Browse projects
          </button>
        </div>
      </ProjectsLayout>
    );
  }

  return (
    <ProjectsLayout activePage="starred">
      <div className="flex-1 overflow-y-auto p-6 md:p-8">
        <h1 className="text-[22px] font-semibold tracking-tight mb-8">Starred</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-10">
          {projects.map(p => (
            <div key={p.id} className="group cursor-pointer flex flex-col relative" onClick={() => navigate(`/projects/${p.id}`)}>
              <div className="aspect-video bg-transparent rounded-xl overflow-hidden mb-3 relative border border-white/10">
                {p.image_url ? (
                  <img src={p.image_url} alt={p.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-white/5 to-white/[0.02]" />
                )}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
                <div className="absolute top-3 right-3">
                  <button onClick={(e) => { e.stopPropagation(); toggleStar(p.id); }} className="bg-[#222]/80 hover:bg-[#333] backdrop-blur-sm p-2 rounded-lg transition-colors">
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  </button>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-orange-600 flex items-center justify-center text-white text-[11px] font-medium shrink-0">{initials}</div>
                <div className="flex flex-col justify-center min-h-[28px] flex-1">
                  <h3 className="text-[#e0e0e0] font-medium text-[14px] leading-tight mb-1 line-clamp-1 group-hover:text-blue-400 transition-colors">{p.name}</h3>
                  <p className="text-[#a0a0a0] text-[12px] leading-tight">{relativeTime(p.updated_at)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </ProjectsLayout>
  );
}
