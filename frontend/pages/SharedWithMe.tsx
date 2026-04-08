import React from 'react';
import { useNavigate } from 'react-router-dom';
import ProjectsLayout from './ProjectsLayout';

export default function SharedWithMe() {
  const navigate = useNavigate();
  return (
    <ProjectsLayout activePage="shared-with-me">
      <div className="flex-1 flex flex-col items-center justify-center p-6 select-none">
        {/* 3D Card illustration */}
        <div className="mb-10 relative w-[200px] h-[140px]" style={{ perspective: '800px' }}>
          <div className="absolute inset-0 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02]"
            style={{ transform: 'rotateY(-15deg) rotateX(8deg)', boxShadow: '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)' }}>
            <div className="p-4 flex flex-col gap-2.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-gradient-to-br from-purple-400/30 to-pink-500/20 border border-purple-400/20 flex items-center justify-center">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                </div>
                <div className="h-2 w-20 rounded-full bg-white/10" />
              </div>
              <div className="h-[60px] rounded-xl bg-white/5 border border-white/5" />
              <div className="flex items-center gap-1.5">
                <div className="w-4 h-4 rounded-full bg-purple-400/20 border border-purple-400/20" />
                <div className="w-4 h-4 rounded-full bg-pink-400/20 border border-pink-400/20 -ml-2" />
                <div className="w-4 h-4 rounded-full bg-blue-400/20 border border-blue-400/20 -ml-2" />
                <div className="h-1.5 w-10 rounded-full bg-white/[0.06] ml-1" />
              </div>
            </div>
          </div>
          <div className="absolute inset-0 rounded-2xl border border-white/5 bg-white/[0.015]"
            style={{ transform: 'rotateY(-15deg) rotateX(8deg) translateZ(-24px) translateX(12px) translateY(8px)' }} />
        </div>

        <h1 className="text-[#f4f4f5] text-[26px] md:text-[30px] font-semibold text-center leading-[1.3] tracking-tight mb-3">
          Projects shared with you<br />
          will appear here
        </h1>
        <p className="text-[#71717a] text-[14px] text-center mb-8">
          When someone shares a project with you, you'll find it in this view.
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
