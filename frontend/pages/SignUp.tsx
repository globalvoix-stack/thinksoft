import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSignUp } from '@clerk/clerk-react';

export default function SignUpPage() {
  const { isLoaded, signUp, setActive } = useSignUp();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState<'email' | 'password' | 'verify'>('email');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoaded) return;
    setError('');

    if (step === 'email') {
      setStep('password');
      return;
    }

    if (step === 'password') {
      setLoading(true);
      try {
        await signUp.create({ emailAddress: email, password });
        await signUp.prepareEmailAddressVerification({ strategy: 'email_code' });
        setStep('verify');
      } catch (err: any) {
        setError(err?.errors?.[0]?.longMessage || err?.errors?.[0]?.message || 'Could not create account.');
      } finally {
        setLoading(false);
      }
      return;
    }

    if (step === 'verify') {
      setLoading(true);
      try {
        const result = await signUp.attemptEmailAddressVerification({ code });
        if (result.status === 'complete') {
          await setActive({ session: result.createdSessionId });
          navigate('/dashboard');
        } else {
          setError('Verification incomplete. Please try again.');
        }
      } catch (err: any) {
        setError(err?.errors?.[0]?.longMessage || err?.errors?.[0]?.message || 'Invalid verification code.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleGoogleSignUp = async () => {
    if (!isLoaded) return;
    try {
      await signUp.authenticateWithRedirect({
        strategy: 'oauth_google',
        redirectUrl: '/sso-callback',
        redirectUrlComplete: '/dashboard',
      });
    } catch (err: any) {
      setError(err?.errors?.[0]?.message || 'Google sign-up failed.');
    }
  };

  return (
    <div className="min-h-screen w-full flex font-sans bg-[#111111] text-white">
      <div className="w-full lg:w-1/2 flex flex-col items-center justify-center relative p-8">
        <div className="w-full max-w-[360px] flex flex-col">
          <h1 className="text-2xl font-bold text-white mb-8 tracking-tight">
            {step === 'verify' ? 'Verify your email' : 'Create your account'}
          </h1>

          {step !== 'verify' && (
            <>
              <div className="mb-6">
                <button
                  type="button"
                  onClick={handleGoogleSignUp}
                  className="w-full bg-transparent hover:bg-[#2a2a2a] text-[#e0e0e0] border border-[#444] rounded-md py-2.5 flex items-center justify-center gap-3 text-sm font-normal transition-colors"
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                    <path fill="#ffffff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#ffffff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#ffffff" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#ffffff" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Continue with Google
                </button>
              </div>

              <div className="flex items-center gap-3 mb-6">
                <div className="h-px bg-[#333] flex-1"></div>
                <span className="text-[#888] text-xs font-normal">OR</span>
                <div className="h-px bg-[#333] flex-1"></div>
              </div>
            </>
          )}

          <form onSubmit={handleContinue} className="flex flex-col gap-4">
            {step === 'verify' ? (
              <div className="flex flex-col">
                <p className="text-[#888] text-sm mb-4">
                  We sent a 6-digit code to <span className="text-white">{email}</span>. Enter it below.
                </p>
                <label className="text-sm font-normal text-white mb-2">Verification code</label>
                <input
                  type="text"
                  placeholder="000000"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  required
                  autoFocus
                  maxLength={6}
                  className="w-full bg-[#111111] border border-[#444] rounded-md px-3 py-2.5 text-sm text-white placeholder-[#888] focus:outline-none focus:border-[#666] tracking-widest text-center"
                />
              </div>
            ) : (
              <>
                <div className="flex flex-col">
                  <label className="text-sm font-normal text-white mb-2">Email</label>
                  <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full bg-[#111111] border border-[#444] rounded-md px-3 py-2.5 text-sm text-white placeholder-[#888] focus:outline-none focus:border-[#666]"
                  />
                </div>

                {step === 'password' && (
                  <div className="flex flex-col">
                    <label className="text-sm font-normal text-white mb-2">Password</label>
                    <input
                      type="password"
                      placeholder="Password (min 8 characters)"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      autoFocus
                      minLength={8}
                      className="w-full bg-[#111111] border border-[#444] rounded-md px-3 py-2.5 text-sm text-white placeholder-[#888] focus:outline-none focus:border-[#666]"
                    />
                  </div>
                )}
              </>
            )}

            {error && <p className="text-red-400 text-sm">{error}</p>}

            <button
              type="submit"
              disabled={loading || !isLoaded}
              className="w-full bg-white text-black rounded-md py-2.5 font-normal text-sm hover:bg-gray-100 transition-colors mt-1 disabled:opacity-60"
            >
              {loading ? 'Please wait...' : step === 'verify' ? 'Verify email' : 'Continue'}
            </button>
          </form>

          <p className="text-[#888] text-sm text-center mt-6">
            Already have an account? <Link to="/login" className="text-white underline font-normal">Log in</Link>
          </p>

          <p className="text-[#888] text-sm text-center mt-4">
            <Link to="/" className="text-[#888] hover:text-white transition-colors">← Back to home</Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:block w-1/2 relative overflow-hidden bg-black">
        <img
          src="/hero-image.png"
          alt="Hero background"
          className="object-cover w-full h-full opacity-90"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex items-center gap-3 text-3xl font-normal text-white drop-shadow-md">
            <span>Creativity runs on</span>
            <div className="flex items-center gap-2 bg-black px-4 py-2 rounded-lg shadow-lg">
              <svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 5.5C7 4.67157 7.67157 4 8.5 4H15.5C16.3284 4 17 4.67157 17 5.5V12H8.5C7.67157 12 7 11.3284 7 10.5V5.5Z" fill="white"/>
                <path d="M17 12H23.5C24.3284 12 25 12.6716 25 13.5V18.5C25 19.3284 24.3284 20 23.5 20H17V12Z" fill="white"/>
                <path d="M7 21.5C7 20.6716 7.67157 20 8.5 20H17V26.5C17 27.3284 16.3284 28 15.5 28H8.5C7.67157 28 7 27.3284 7 26.5V21.5Z" fill="white"/>
              </svg>
              <span className="font-normal tracking-tight">Thinksoft</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
