import React, { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth, useUser } from '@clerk/clerk-react';
import { ArrowLeft, Send, Star, Loader2, CheckCircle, AlertCircle, FileCode2, ChevronDown, ChevronRight } from 'lucide-react';
import { makeApi, type Project, type SseProgressEvent, type GeneratedFile } from '../lib/api';

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

const MODE_BADGE: Record<string, { label: string; className: string }> = {
  light: { label: 'Light', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  autonomous: { label: 'Autonomous', className: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  max: { label: 'Max', className: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
};

function FileTree({ files }: { files: GeneratedFile[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<string | null>(null);

  const dirs = new Map<string, GeneratedFile[]>();
  for (const f of files) {
    const parts = f.file_path.split('/');
    const dir = parts.length > 1 ? parts.slice(0, -1).join('/') : '';
    if (!dirs.has(dir)) dirs.set(dir, []);
    dirs.get(dir)!.push(f);
  }

  const selectedFile = files.find(f => f.file_path === selected);

  return (
    <div className="flex gap-4 h-full min-h-0">
      {/* File list */}
      <div className="w-64 flex-shrink-0 overflow-y-auto border border-white/10 rounded-xl bg-[#111] p-2">
        {files.map(f => {
          const parts = f.file_path.split('/');
          const name = parts[parts.length - 1];
          return (
            <button
              key={f.id}
              onClick={() => setSelected(f.file_path)}
              className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-left text-[13px] transition-colors ${selected === f.file_path ? 'bg-white/10 text-white' : 'text-[#a0a0a0] hover:text-white hover:bg-white/5'}`}
            >
              <FileCode2 className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="truncate">{f.file_path}</span>
            </button>
          );
        })}
      </div>

      {/* File content */}
      <div className="flex-1 overflow-auto border border-white/10 rounded-xl bg-[#111]">
        {selectedFile ? (
          <div className="p-4">
            <div className="text-[12px] text-[#888] mb-3 font-mono">{selectedFile.file_path}</div>
            <pre className="text-[13px] text-[#e0e0e0] font-mono whitespace-pre-wrap leading-relaxed">
              {selectedFile.content}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-[#555] text-[13px]">
            Select a file to view its contents
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProjectView() {
  const { id: projectId } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { getToken } = useAuth();
  const { user } = useUser();

  const [project, setProject] = useState<Project | null>(null);
  const [files, setFiles] = useState<GeneratedFile[]>([]);
  const [jobStatus, setJobStatus] = useState<'running' | 'done' | 'error' | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [jobError, setJobError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [prompt, setPrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const cleanupRef = useRef<(() => void) | null>(null);
  const initials = (user?.firstName?.[0] || user?.emailAddresses?.[0]?.emailAddress?.[0] || 'U').toUpperCase();

  // Load project and optionally start streaming a job
  useEffect(() => {
    if (!projectId) return;
    const api = makeApi(() => getToken());
    const jobId = searchParams.get('job_id');

    Promise.all([
      api.projects.list().then(list => list.find(p => p.id === projectId) ?? null),
      api.files.forProject(projectId),
    ])
      .then(([proj, fileList]) => {
        setProject(proj);
        setFiles(fileList);
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));

    if (jobId) {
      setJobStatus('running');
      const cleanup = api.streamJob(projectId, jobId, (event: SseProgressEvent) => {
        if (event.type === 'progress') {
          setProgress(event.progress ?? 0);
          setCurrentStep(event.current_step ?? null);
        } else if (event.type === 'done') {
          setJobStatus('done');
          setProgress(100);
          // Refresh files
          api.files.forProject(projectId).then(setFiles).catch(() => {});
          if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
        } else if (event.type === 'error') {
          setJobStatus('error');
          setJobError(event.error ?? 'Generation failed');
          if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
        }
      }, getToken);
      cleanupRef.current = cleanup;
    }

    return () => {
      if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
    };
  }, [projectId]);

  const handleSubmit = async () => {
    const text = prompt.trim();
    if (!text || isSubmitting || !projectId) return;
    setIsSubmitting(true);
    setSubmitError('');
    try {
      const api = makeApi(() => getToken());
      const gen = await api.generate({ project_id: projectId, prompt: text, mode: 'autonomous' });
      setPrompt('');
      setJobStatus('running');
      setProgress(0);
      setCurrentStep(null);

      if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
      const cleanup = api.streamJob(projectId, gen.job_id, (event: SseProgressEvent) => {
        if (event.type === 'progress') {
          setProgress(event.progress ?? 0);
          setCurrentStep(event.current_step ?? null);
        } else if (event.type === 'done') {
          setJobStatus('done');
          setProgress(100);
          api.files.forProject(projectId).then(setFiles).catch(() => {});
          if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
        } else if (event.type === 'error') {
          setJobStatus('error');
          setJobError(event.error ?? 'Generation failed');
          if (cleanupRef.current) { cleanupRef.current(); cleanupRef.current = null; }
        }
      }, getToken);
      cleanupRef.current = cleanup;
    } catch (err: any) {
      setSubmitError(err.message || 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  const onKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex flex-col items-center justify-center gap-4 text-white">
        <p className="text-[#888]">Project not found.</p>
        <button onClick={() => navigate('/all-projects')} className="text-[13px] text-blue-400 hover:underline">Back to projects</button>
      </div>
    );
  }

  const modeBadge = MODE_BADGE[project.mode] ?? MODE_BADGE['autonomous'];

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white font-sans flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-4 px-6 py-4 border-b border-white/5">
        <button onClick={() => navigate('/all-projects')} className="text-[#a0a0a0] hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <h1 className="text-[18px] font-semibold truncate">{project.name}</h1>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${modeBadge.className}`}>
            {modeBadge.label}
          </span>
        </div>
        <div className="flex items-center gap-3 text-[#888] text-[13px]">
          <span>Updated {relativeTime(project.updated_at)}</span>
        </div>
      </div>

      {/* Job progress banner */}
      {jobStatus === 'running' && (
        <div className="px-6 py-3 bg-blue-500/10 border-b border-blue-500/20 flex items-center gap-3">
          <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[13px] text-blue-300">{currentStep || 'Generating…'}</span>
              <span className="text-[12px] text-blue-400">{progress}%</span>
            </div>
            <div className="h-1 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
            </div>
          </div>
        </div>
      )}
      {jobStatus === 'done' && (
        <div className="px-6 py-3 bg-green-500/10 border-b border-green-500/20 flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-400" />
          <span className="text-[13px] text-green-300">Generation complete</span>
        </div>
      )}
      {jobStatus === 'error' && (
        <div className="px-6 py-3 bg-red-500/10 border-b border-red-500/20 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400" />
          <span className="text-[13px] text-red-300">{jobError || 'Generation failed'}</span>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {files.length > 0 ? (
          <div className="flex-1 p-6 min-h-0">
            <h2 className="text-[13px] font-semibold text-[#a0a0a0] mb-4 tracking-wide uppercase">Generated Files ({files.length})</h2>
            <div className="h-[calc(100%-2.5rem)]">
              <FileTree files={files} />
            </div>
          </div>
        ) : jobStatus !== 'running' ? (
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
            <FileCode2 className="w-12 h-12 text-[#333] mb-4" />
            <p className="text-[#555] text-[14px]">No files generated yet.</p>
            <p className="text-[#444] text-[13px] mt-1">Use the input below to generate your project.</p>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
          </div>
        )}
      </div>

      {/* Prompt input */}
      <div className="px-6 py-4 border-t border-white/5">
        {submitError && <p className="text-red-400 text-[13px] mb-2">{submitError}</p>}
        <div className="relative flex items-end gap-3 bg-[#161616] border border-white/10 rounded-2xl px-4 py-3 focus-within:border-white/25 transition-colors">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={onKey}
            placeholder="Describe changes or additions…"
            rows={1}
            className="flex-1 bg-transparent text-[14px] text-white placeholder:text-[#555] resize-none outline-none leading-relaxed max-h-40 overflow-y-auto"
            style={{ fieldSizing: 'content' } as React.CSSProperties}
          />
          <button
            onClick={handleSubmit}
            disabled={!prompt.trim() || isSubmitting || jobStatus === 'running'}
            className="flex-shrink-0 w-8 h-8 rounded-xl bg-white text-black flex items-center justify-center transition-opacity disabled:opacity-30 hover:opacity-90"
          >
            {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
        <p className="text-[#555] text-[11px] mt-2 px-1">Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}
