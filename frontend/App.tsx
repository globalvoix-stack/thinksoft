/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useAuth, useClerk } from '@clerk/clerk-react';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import Dashboard from './pages/Dashboard';
import AllProjects from './pages/AllProjects';
import Starred from './pages/Starred';
import CreatedByMe from './pages/CreatedByMe';
import SharedWithMe from './pages/SharedWithMe';
import { ChevronDown, Plus, Map, Mic, ArrowUp, Users, Database, HardDrive, Bell, Zap, Globe, Shield, Lock, ShieldAlert, ArrowRightLeft, CheckCircle2, Activity, FileText } from 'lucide-react';
import { motion } from 'motion/react';
// @ts-ignore
import bgImage from './background.png.png';
// @ts-ignore
import scene1Video from './scene1.mp4.webm';
// @ts-ignore
import scene2Video from './scene2.mp4.webm';
// @ts-ignore
import scene3Video from './scene3.mp4.webm';
// @ts-ignore
import authImg from './auth.png';
// @ts-ignore
import databasesImg from './databases.png';
// @ts-ignore
import storageImg from './storage.png';
// @ts-ignore
import notificationsImg from './notifications.png';
// @ts-ignore
import realtimeImg from './realtime.png';
// @ts-ignore
import hostingImg from './hosting.png';
// @ts-ignore
import ctaBgImg from './cta-bg.png';

const SCENE_VIDEOS = [
  scene1Video,
  scene2Video,
  scene3Video
];

function NavButtons() {
  const { isSignedIn } = useAuth();
  if (isSignedIn) {
    return (
      <div className="flex items-center gap-3">
        <Link to="/dashboard" className="text-[14px] font-medium px-[14px] py-[8px] rounded-[10px] border border-white/10 hover:bg-white/10 transition-colors">
          Dashboard
        </Link>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-3">
      <Link to="/login" className="text-[14px] font-medium px-[14px] py-[8px] rounded-[10px] border border-white/10 hover:bg-white/10 transition-colors">
        Log in
      </Link>
      <Link to="/signup" className="text-[14px] font-medium px-[16px] py-[8px] rounded-[10px] bg-white text-black hover:bg-gray-200 transition-colors">
        Get started
      </Link>
    </div>
  );
}

function LandingPage() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [prompt, setPrompt] = useState('');

  const handleVideoEnded = () => {
    setActiveIndex((prev) => (prev + 1) % SCENE_VIDEOS.length);
  };

  const handleFeatureClick = (index: number) => {
    setActiveIndex(index);
  };

  return (
    <div className="w-full font-sans text-white bg-[#171717] overflow-x-hidden">
      {/* Hero Section */}
      <div 
        className="min-h-screen w-full flex flex-col relative"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat'
        }}
      >
        {/* Navigation */}
      <nav className="relative z-20 flex items-center justify-between px-6 py-5 w-full">
        <div className="flex items-center gap-8">
          {/* Logo */}
          <div className="flex items-center gap-2 cursor-pointer">
            <span className="text-xl font-bold tracking-tight">Thinksoft</span>
          </div>

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-6 text-[15px] font-medium text-gray-200">
            <button className="flex items-center gap-1 hover:text-white transition-colors">
              Solutions <ChevronDown className="w-4 h-4 text-gray-400" />
            </button>
            <button className="flex items-center gap-1 hover:text-white transition-colors">
              Resources <ChevronDown className="w-4 h-4 text-gray-400" />
            </button>
            <a href="#" className="hover:text-white transition-colors">Enterprise</a>
            <a href="#" className="hover:text-white transition-colors">Pricing</a>
            <a href="#" className="hover:text-white transition-colors">Community</a>
            <a href="#" className="hover:text-white transition-colors">Security</a>
          </div>
        </div>

        {/* Auth Buttons */}
        <NavButtons />
      </nav>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 mt-[-8vh]">
        <div className="text-center mb-8">
          <motion.h1
            initial={{ y: 30 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
            className="text-4xl md:text-[48px] font-bold tracking-tight"
          >
            {"Ready to build?".split("").map((char, index, array) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
                animate={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.03 + 0.1, ease: 'easeOut' }}
                className="relative inline-block"
              >
                <span className="text-white">{char === " " ? "\u00A0" : char}</span>
                <motion.span
                  initial={{ opacity: 1 }}
                  animate={{ opacity: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.03 + 0.5, ease: 'easeInOut' }}
                  className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                  style={{
                    backgroundSize: `${array.length * 100}% 100%`,
                    backgroundPosition: `${(index / (array.length - 1)) * 100}% 0`
                  }}
                >
                  {char === " " ? "\u00A0" : char}
                </motion.span>
              </motion.span>
            ))}
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
            className="text-lg md:text-[20px] text-gray-400 font-medium mt-6"
          >
            Create apps and websites by chatting with AI
          </motion.p>
        </div>

        {/* Prompt Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
          className="w-full max-w-[720px] bg-[#262626] rounded-[24px] border border-white/5 p-3 shadow-2xl flex flex-col min-h-[120px]"
        >
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full bg-transparent text-white placeholder-[#A3A3A3] resize-none outline-none text-[15px] flex-1 p-2"
            placeholder="Ask Thinksoft to create a landing page for my..."
            spellCheck={false}
          />
          
          <div className="flex items-center justify-between mt-2 px-2 pb-1">
            <button className="w-8 h-8 rounded-full border border-[#4A4A4A] flex items-center justify-center hover:bg-white/5 transition-colors text-[#A3A3A3]">
              <Plus className="w-4 h-4" />
            </button>
            
            <div className="flex items-center gap-4">
              <button className="text-[#A3A3A3] hover:text-white transition-colors">
                <Map className="w-4 h-4" />
              </button>
              <button className="text-[#A3A3A3] hover:text-white transition-colors">
                <Mic className="w-4 h-4" />
              </button>
              <button className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ml-1 ${prompt.trim() ? 'bg-white text-[#1A1A1A] hover:bg-gray-200' : 'bg-[#9CA3AF] text-[#1A1A1A] hover:bg-[#D1D5DB]'}`}>
                <ArrowUp className="w-4 h-4" />
              </button>
            </div>
          </div>
        </motion.div>
      </main>
      </div>

      {/* Meet Thinksoft Section */}
      <section className="w-full bg-[#1A1A1A] py-32">
        <div className="max-w-7xl mx-auto px-6">
          <motion.h2 
            initial={{ y: 30 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="text-4xl md:text-5xl font-bold mb-16 tracking-tight"
          >
          {"Meet Thinksoft".split("").map((char, index, array) => (
            <motion.span
              key={index}
              initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
              whileInView={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.3, delay: index * 0.03 + 0.1, ease: 'easeOut' }}
              className="relative inline-block"
            >
              <span className="text-white">{char === " " ? "\u00A0" : char}</span>
              <motion.span
                initial={{ opacity: 1 }}
                whileInView={{ opacity: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.6, delay: index * 0.03 + 0.5, ease: 'easeInOut' }}
                className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                style={{
                  backgroundSize: `${array.length * 100}% 100%`,
                  backgroundPosition: `${(index / (array.length - 1)) * 100}% 0`
                }}
              >
                {char === " " ? "\u00A0" : char}
              </motion.span>
            </motion.span>
          ))}
        </motion.h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Left: Video */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-7 relative aspect-square md:aspect-[4/3] lg:aspect-square bg-[#111111] rounded-2xl overflow-hidden border border-white/5 shadow-2xl"
          >
            {/* Uploaded video */}
            <video 
              key={activeIndex}
              onEnded={handleVideoEnded}
              autoPlay 
              muted 
              playsInline
              className="w-full h-full object-cover"
            >
              <source src={SCENE_VIDEOS[activeIndex]} />
            </video>
          </motion.div>
          
          {/* Right: Features */}
          <div className="lg:col-span-5 flex flex-col gap-10">
            {[
              {
                title: "Start with an idea",
                description: "Describe the app or website you want to create or drop in screenshots and docs"
              },
              {
                title: "Watch it come to life",
                description: "See your vision transform into a working prototype in real-time as AI builds it for you"
              },
              {
                title: "Refine and ship",
                description: "Iterate on your creation with simple feedback and deploy it to the world with one click"
              }
            ].map((feature, index) => (
              <motion.div 
                key={index}
                onClick={() => handleFeatureClick(index)}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.8, delay: 0.2 + index * 0.1, ease: [0.16, 1, 0.3, 1] }}
                className="flex flex-col gap-2 cursor-pointer group"
              >
                <h3 className={`text-2xl md:text-[28px] font-bold tracking-tight transition-colors duration-300 ${activeIndex === index ? 'text-white' : 'text-[#737373] group-hover:text-white'}`}>{feature.title}</h3>
                <p className={`text-lg md:text-[18px] leading-relaxed transition-colors duration-300 ${activeIndex === index ? 'text-[#A3A3A3]' : 'text-[#525252] group-hover:text-[#737373]'}`}>
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
        </div>
      </section>

      {/* Bento Grid Section */}
      <section className="w-full bg-[#171717] py-32 px-6 text-white border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.h2
            initial={{ y: 30 }}
            whileInView={{ y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="text-3xl md:text-4xl lg:text-5xl font-medium tracking-tight mb-12 max-w-2xl leading-[1.1]"
          >
            {"Everything you need to".split("").map((char, index, array) => (
              <motion.span
                key={index}
                initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
                whileInView={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.3, delay: index * 0.03 + 0.1, ease: 'easeOut' }}
                className="relative inline-block"
              >
                <span className="text-white">{char === " " ? "\u00A0" : char}</span>
                <motion.span
                  initial={{ opacity: 1 }}
                  whileInView={{ opacity: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.6, delay: index * 0.03 + 0.5, ease: 'easeInOut' }}
                  className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                  style={{ backgroundSize: `${array.length * 100}% 100%`, backgroundPosition: `${(index / (array.length - 1)) * 100}% 0` }}
                >
                  {char === " " ? "\u00A0" : char}
                </motion.span>
              </motion.span>
            ))}
            <br />
            {"build a real product".split("").map((char, index, array) => (
              <motion.span
                key={`b${index}`}
                initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
                whileInView={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.3, delay: (index + 22) * 0.03 + 0.1, ease: 'easeOut' }}
                className="relative inline-block"
              >
                <span className="text-white">{char === " " ? "\u00A0" : char}</span>
                <motion.span
                  initial={{ opacity: 1 }}
                  whileInView={{ opacity: 0 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.6, delay: (index + 22) * 0.03 + 0.5, ease: 'easeInOut' }}
                  className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                  style={{ backgroundSize: `${array.length * 100}% 100%`, backgroundPosition: `${(index / (array.length - 1)) * 100}% 0` }}
                >
                  {char === " " ? "\u00A0" : char}
                </motion.span>
              </motion.span>
            ))}
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
            {/* Auth */}
            <div className="col-span-1 md:col-span-3 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <Users className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Auth</h3>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                Authenticate users securely with multiple login methods like <span className="font-medium text-white">Email/Password, SMS, OAuth, Anonymous, and Magic URLs.</span>
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[300px] border border-white/5">
                <img src={authImg} alt="Auth UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Databases */}
            <div className="col-span-1 md:col-span-3 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <Database className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Databases</h3>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                <span className="font-medium text-white">Scalable and robust databases</span> backed by your favorite technologies.
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[300px] border border-white/5">
                <img src={databasesImg} alt="Databases UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Storage */}
            <div className="col-span-1 md:col-span-2 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <HardDrive className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Storage</h3>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                Securely store files with <span className="font-medium text-white">advanced compression, encryption and image transformations.</span>
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[240px] border border-white/5">
                <img src={storageImg} alt="Storage UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Notifications */}
            <div className="col-span-1 md:col-span-2 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <Bell className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Notifications</h3>
                <span className="ml-2 px-2 py-0.5 text-[11px] font-medium bg-[#171717] text-[#A3A3A3] rounded-full border border-white/10 uppercase tracking-wider">Coming soon</span>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                Send real-time updates and alerts to users through email or SMS.
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[240px] border border-white/5">
                <img src={notificationsImg} alt="Notifications UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Realtime */}
            <div className="col-span-1 md:col-span-2 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <Zap className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Realtime</h3>
                <span className="ml-2 px-2 py-0.5 text-[11px] font-medium bg-[#171717] text-[#A3A3A3] rounded-full border border-white/10 uppercase tracking-wider">Coming soon</span>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                Build collaborative, dynamic experiences that update instantly for every user.
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[240px] border border-white/5">
                <img src={realtimeImg} alt="Realtime UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Hosting */}
            <div className="col-span-1 md:col-span-3 bg-[#111111] rounded-[32px] p-8 flex flex-col border border-white/5 shadow-sm">
              <div className="flex items-center gap-2.5 mb-3">
                <Globe className="w-5 h-5 text-white" />
                <h3 className="text-xl font-medium text-white tracking-tight">Hosting</h3>
              </div>
              <p className="text-[#A3A3A3] text-[15px] mb-6 leading-relaxed">
                Host and maintain <span className="font-medium text-white">your website domains and frontend code.</span> Integrated with all Appwrite products.
              </p>
              <div className="mt-auto bg-[#171717] rounded-2xl overflow-hidden flex items-center justify-center min-h-[300px] border border-white/5">
                <img src={hostingImg} alt="Hosting UI" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
            </div>

            {/* Dark CTA */}
            <div className="col-span-1 md:col-span-3 bg-[#111111] rounded-[32px] p-10 flex flex-col justify-end relative overflow-hidden text-white min-h-[400px] border border-white/5">
              <div className="absolute inset-0 opacity-50">
                <img src={ctaBgImg} alt="" className="w-full h-full object-cover" onError={(e) => e.currentTarget.style.display = 'none'} />
              </div>
              <div className="relative z-10">
                <h3 className="text-3xl md:text-4xl font-medium tracking-tight mb-6 leading-[1.1]">
                  It's in your imagination.<br />Now build it.
                </h3>
                <Link to="/signup" className="px-6 py-3 bg-white text-black text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors w-fit inline-block">
                  Start now
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security & Compliance Section */}
      <section className="w-full bg-[#111111] py-32 px-6 text-white border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-24 mb-20">
            <motion.h2
              initial={{ y: 30 }}
              whileInView={{ y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              className="text-3xl md:text-4xl lg:text-[40px] font-medium tracking-tight leading-[1.1]"
            >
              {"Safely scale with built-in".split("").map((char, index, array) => (
                <motion.span
                  key={index}
                  initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
                  whileInView={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.3, delay: index * 0.03 + 0.1, ease: 'easeOut' }}
                  className="relative inline-block"
                >
                  <span className="text-white">{char === " " ? "\u00A0" : char}</span>
                  <motion.span
                    initial={{ opacity: 1 }}
                    whileInView={{ opacity: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.6, delay: index * 0.03 + 0.5, ease: 'easeInOut' }}
                    className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                    style={{ backgroundSize: `${array.length * 100}% 100%`, backgroundPosition: `${(index / (array.length - 1)) * 100}% 0` }}
                  >
                    {char === " " ? "\u00A0" : char}
                  </motion.span>
                </motion.span>
              ))}
              <br />
              {"security and compliance".split("").map((char, index, array) => (
                <motion.span
                  key={`s${index}`}
                  initial={{ opacity: 0, filter: 'blur(8px)', scale: 0.95 }}
                  whileInView={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.3, delay: (index + 26) * 0.03 + 0.1, ease: 'easeOut' }}
                  className="relative inline-block"
                >
                  <span className="text-white">{char === " " ? "\u00A0" : char}</span>
                  <motion.span
                    initial={{ opacity: 1 }}
                    whileInView={{ opacity: 0 }}
                    viewport={{ once: true, margin: "-100px" }}
                    transition={{ duration: 0.6, delay: (index + 26) * 0.03 + 0.5, ease: 'easeInOut' }}
                    className="absolute left-0 top-0 bg-[linear-gradient(90deg,#3b82f6,#6366f1,#a855f7,#ec4899,#ef4444,#f97316,#eab308)] bg-clip-text text-transparent"
                    style={{ backgroundSize: `${array.length * 100}% 100%`, backgroundPosition: `${(index / (array.length - 1)) * 100}% 0` }}
                  >
                    {char === " " ? "\u00A0" : char}
                  </motion.span>
                </motion.span>
              ))}
            </motion.h2>
            <div className="flex items-center">
              <p className="text-base md:text-[17px] text-[#A3A3A3] leading-relaxed">
                With a security-first approach, we ensure your products and users are safe by default, making it easy for you to adhere to strict safety policies.
              </p>
            </div>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 border-t border-l border-dotted border-white/15">
            {/* Item 1: DDoS */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <Shield className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">DDoS</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Automatically detect and mitigate Distributed Denial-of-Service (DDoS) attacks.
              </p>
            </div>
            
            {/* Item 2: Encryption */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <Lock className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">Encryption</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Built-in data encryption both in rest and in transit.
              </p>
            </div>
            
            {/* Item 3: Abuse protection */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <ShieldAlert className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">Abuse protection</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Protect your APIs from abuse with built-in protection.
              </p>
            </div>
            
            {/* Item 4: Data migrations */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <ArrowRightLeft className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">Data migrations</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Easily transfer data from 3rd parties or between Cloud and self-hosted.
              </p>
            </div>
            
            {/* Item 5: GDPR */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <Globe className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">GDPR</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Safeguard user data and privacy with provided GDPR regulations.
              </p>
            </div>
            
            {/* Item 6: SOC-2 */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <CheckCircle2 className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">SOC-2</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Ensure the highest level of security and privacy protection.
              </p>
            </div>
            
            {/* Item 7: HIPAA */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <Activity className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">HIPAA</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Protect sensitive user health data.
              </p>
            </div>
            
            {/* Item 8: CCPA */}
            <div className="p-8 md:p-10 border-b border-r border-dotted border-white/15">
              <FileText className="w-5 h-5 mb-4 text-white" strokeWidth={1.5} />
              <h3 className="text-base md:text-[17px] font-medium mb-2.5 text-white">CCPA</h3>
              <p className="text-[14px] text-[#A3A3A3] leading-relaxed">
                Protect sensitive user health data.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function SSOCallback() {
  const { handleRedirectCallback } = useClerk();
  React.useEffect(() => {
    handleRedirectCallback({
      afterSignInUrl: '/dashboard',
      afterSignUpUrl: '/dashboard',
    });
  }, []);
  return (
    <div className="min-h-screen bg-[#111111] flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin" />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/all-projects" element={<AllProjects />} />
        <Route path="/starred" element={<Starred />} />
        <Route path="/created-by-me" element={<CreatedByMe />} />
        <Route path="/shared-with-me" element={<SharedWithMe />} />
        <Route path="/sso-callback" element={<SSOCallback />} />
      </Routes>
    </BrowserRouter>
  );
}
