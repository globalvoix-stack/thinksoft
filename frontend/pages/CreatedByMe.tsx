import React from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectsLayout from './ProjectsLayout';

export default function CreatedByMe() {
  const navigate = useNavigate();
  return (
    <ProjectsLayout activePage="created-by-me">
      <div className="flex-1 flex flex-col items-center justify-center p-6 select-none">
        {/* 3D Card illustration */}
        <div className="mb-10 relative w-[200px] h-[140px]" style={{ perspective: '800px' }}>
          <div className="absolute inset-0 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02]"
            style={{ transform: 'rotateY(-15deg) rotateX(8deg)', boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)' }}>
            <div className="p-4 flex flex-col gap-2.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-400/30 to-indigo-500/20 border border-blue-400/20 flex items-center justify-center">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-blue-400">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" />
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
          Projects you create will<br />
          appear here
        </h1>
        <p className="text-[#71717a] text-[14px] text-center mb-8">
          Start a new project and it will show up in this view.
        </p>
        <button
          onClick={() => navigate('/all-projects')}
          className="px-4 py-2 bg-transparent border border-[#3f3f46] rounded-lg text-sm font-medium text-[#e4e4e7] hover:bg-[#27272a] hover:text-white transition-all duration-200 shadow-sm"
        >
          Browse projects
        </button>
      </div>
    </ProjectsLayout>
  );
}
