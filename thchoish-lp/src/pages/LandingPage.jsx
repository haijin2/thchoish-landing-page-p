import React, { useEffect, useState } from "react";
import emailjs from "@emailjs/browser";

import ALMV from '../assets/ALMV.png';
import angelaImg from '../assets/angela.png';
import licelleImg from '../assets/licelle.jpg';
import markImg from '../assets/mark.jpeg';
import vhillyImg from '../assets/vhilly.png'; 

import { motion, useAnimation } from "framer-motion";
import { useInView } from "react-intersection-observer";

// Lines 9 to 34 control the animation wrapper. Nothing to adjust here unless you wish :) 
const FadeInSection = ({ children, offset = 40, delay = 0 }) => {
  const controls = useAnimation();
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.2 });

  useEffect(() => {
    if (inView) controls.start("visible");
  }, [controls, inView]);

  const variants = {
    hidden: { opacity: 0, y: offset },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, delay, ease: "easeOut" } },
  };

  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={controls}
      variants={variants}
      className="will-change-transform"
    >
      {children}
    </motion.div>
  );
};

// ------------------ SubscribeBlock (client -> EmailJS + optional backend POST) ------------------
// This component will attempt to send an EmailJS email AND (if API_BASE is provided) POST the email to your backend.
function SubscribeBlock() {
  const [status, setStatus] = useState(null); // null | 'sending' | 'success' | 'error' | 'invalid'
  const [sending, setSending] = useState(false);

  // If REACT_APP_API_BASE is not provided, this will skip the backend POST.
  const API_BASE = process.env.REACT_APP_API_BASE || '';

  // EmailJS env vars
  const SERVICE_ID = process.env.REACT_APP_EMAILJS_SERVICE_ID;
  const TEMPLATE_ID = process.env.REACT_APP_EMAILJS_TEMPLATE_ID;
  const PUBLIC_KEY = process.env.REACT_APP_EMAILJS_PUBLIC_KEY;

  // Initialize EmailJS once if public key is present
  useEffect(() => {
    if (PUBLIC_KEY) {
      try {
        emailjs.init(PUBLIC_KEY);
      } catch (err) {
        // init can sometimes throw in weird environments; we'll still try send with the public key in send
        console.warn('emailjs.init warning:', err);
      }
    }
  }, [PUBLIC_KEY]);

  async function onSubmit(e) {
    e.preventDefault();
    const email = e.target.email.value?.trim();
    if (!email) return setStatus('invalid');

    // Basic client-side validation
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(email)) return setStatus('invalid');

    setStatus('sending');
    setSending(true);

    let emailjsSuccess = false;
    let backendSuccess = false;

    // Prepare template params for EmailJS (ensure your EmailJS template uses 'user_email')
    const templateParams = {
      user_email: email,
      // add other template variables here if your template expects them, e.g. user_name
    };

    // 1) Try EmailJS (client-side)
    try {
      if (SERVICE_ID && TEMPLATE_ID) {
        const res = await emailjs.send(SERVICE_ID, TEMPLATE_ID, templateParams, PUBLIC_KEY);
        // EmailJS typical successful response has status 200
        if (res?.status === 200) {
          emailjsSuccess = true;
        } else {
          console.warn('EmailJS unexpected response:', res);
        }
      } else {
        console.warn('EmailJS environment variables missing (SERVICE_ID/TEMPLATE_ID) — skipping EmailJS send.');
      }
    } catch (err) {
      console.error('EmailJS send error:', err);
    }

    // 2) Try backend POST if API_BASE configured
    try {
      if (API_BASE) {
        const res2 = await fetch(`${API_BASE}/api/subscribe`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });
        if (res2.ok) {
          backendSuccess = true;
        } else {
          const data = await res2.json().catch(() => ({}));
          console.error('Backend subscribe error:', data);
        }
      } else {
        // No backend configured — that's fine if EmailJS handled it.
        console.info('No API_BASE provided — skipping backend POST.');
      }
    } catch (err) {
      console.error('Backend POST error:', err);
    }

    setSending(false);

    if (emailjsSuccess || backendSuccess) {
      setStatus('success');
      e.target.reset();
    } else {
      setStatus('error');
    }
  }

  return (
    <section id="subscribe" className="py-12 px-8 max-w-md mx-auto text-center">
      <h2 className="text-5xl text-[#EC4F2F] font-semibold text-left mb-2 tracking-wide">
        Stay Connected!
      </h2>
      <p className="text-gray-400 text-2xl text-left mb-6 leading-relaxed">
        Join our research community to receive updates on ALMV developments.
      </p>

      <form onSubmit={onSubmit} className="flex max-w-md mx-auto">
        <input
          name="email"
          type="email"
          placeholder="Enter your email address"
          required
          className="flex-1 bg-[#1f1f1f]/80 border border-white/20 text-white placeholder-gray-400 px-4 py-3 rounded-l-xl shadow-inner focus:outline-none"
        />
        <button
          type="submit"
          disabled={sending}
          className={"px-6 py-3 rounded-r-xl font-semibold text-white border border-white/20 " +
            (sending ? 'opacity-60 cursor-wait bg-gray-600' : 'bg-gradient-to-r from-[#E04333]/80 to-[#6A2F67]/80')}
        >
          {sending ? 'Sending…' : 'Subscribe'}
        </button>
      </form>

      <div className="mt-3">
        {status === 'sending' && <span>Sending…</span>}
        {status === 'success' && <span className="text-green-400">Thanks, you are subscribed to our update newsletter.</span>}
        {status === 'error' && <span className="text-red-400">Something went wrong. Try again later.</span>}
        {status === 'invalid' && <span className="text-yellow-400">Please enter a valid email.</span>}
      </div>
    </section>
  );
}

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="bg-[#252219] text-white font-sans min-h-screen">
      
      {/* Header */}
      <header
        className="sticky top-0 z-50 flex justify-between items-center px-8 py-4 backdrop-blur-sm border-b border-gray-700 bg-[#1D1A13]/90"
      > 
      
       <div className="flex items-center gap-3 mb-3 select-none cursor-default">
          <img
            src={ALMV} 
            alt="ALMV Logo"
            className="w-20 h-20"
          />

          <div className="flex flex-col items-start gap-1">
            <div className="text-4xl font-extrabold bg-gradient-to-r from-[#E04333] to-[#6A2F67] bg-clip-text text-transparent">
              ALMV
            </div>
            <p className="text-sm text-white">
              Cryptography + Steganography
            </p>
          </div>
        </div>



        <nav className="space-x-6 text-sm font-medium text-white">
          <a href="https://github.com/haijin2/thchoish-landing-page/releases/download/v.1.1/almv.exe" className="hover:text-red-500 transition-colors duration-300">Download</a>
          <a href="#features" className="hover:text-red-500 transition-colors duration-300">Features</a>
          <a href="#workflow" className="hover:text-red-500 transition-colors duration-300">Learn How it Works</a>
          <a href="#team" className="hover:text-red-500 transition-colors duration-300">Team</a>
          <a href="#subscribe" className="hover:text-red-500 transition-colors duration-300">Subscription</a>
        </nav>

      </header>
        
      {/* Hero Section */}
      <FadeInSection offset={50}>
        <section id="download" className="text-center py-10 px-6 max-w-4xl mx-auto">
          <h1 className="text-[6rem] sm:text-[8rem] md:text-[10rem] lg:text-[14rem] font-extrabold bg-gradient-to-r from-[#E04333] to-[#6A2F67] bg-clip-text text-transparent select-none tracking-tight">
          ALMV
        </h1>

          <p className="text-white-1000 text-3xl mt--0 mb-0 leading-relaxed">
            Cryptography + Steganography. 
          </p>
          <p className="text-white-300 text-lg mb-8 leading-relaxed">
            The only freeware that secures your image metadata in plain sight.
          </p>
          <div className="inline-flex gap-4">
    <button
      onClick={() =>
        window.open(
          "https://github.com/haijin2/thchoish-landing-page/releases/download/v.1.1/almv.ex"
        )
      }
      className="bg-gradient-to-r from-[#E04333]/80 to-[#6A2F67]/80 
        backdrop-blur-md 
        px-6 py-3 rounded-xl 
        font-semibold text-white 
        shadow-lg shadow-[#E04333]/30 
        hover:shadow-xl hover:scale-105 
        transition-all duration-300 
        border border-white/20"
    >
      Download ALMV
    </button>


              <button className="bg-gradient-to-r from-[#E04333]/80 to-[#6A2F67]/80 
              backdrop-blur-md 
              px-6 py-3 rounded-xl 
              font-semibold text-white 
              shadow-lg shadow-[#E04333]/30 
              hover:shadow-xl hover:scale-105 
              transition-all duration-300 
              border border-white/20">              
              Read the official documentation
            </button>
          </div>

          {/* newly added */}
          <div className="inline-flex gap-4 mt-6">
            {[("✓ Metadata Extraction"), ("✓ Advanced Encryption"), ("✓ Invisible Embedding"), ("✓ Free & Privacy-Focused")].map((text, i) => (
              <div
                key={i}
                className="relative px-4 py-5 rounded-lg font-xs text-gray-300
                  before:absolute before:inset-[-1px]
                  before:rounded-lg
                  before:bg-gradient-to-r before:from-[#E04333] before:to-[#6A2F67]
                  before:-z-10
                  bg-[#2e2e2e]
                  shadow-md hover:border-red-500 transition-colors duration-300 cursor-default"
              >
                {text}
              </div>
            ))}
          </div>


        </section>
      </FadeInSection>




      {/* Focus Section */}
      <FadeInSection offset={40} delay={0.1}>
      <section id="features" className="mt-4 mb-4 bg-[#121212] py-10 px-8 max-w-6xl mx-auto rounded-lg"
      >
    <h2 className="text-5xl font-semibold text-left mb-3 tracking-wide text-[#EC4F2F]">
      Focus on taking and sending photos.
    </h2>

    <p className="text-2xl text-gray-200 mb-6">
      ALMV will take care of the rest.
    </p>

    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
      {[
        {
          title: "AES-256 Encryption",
          desc: "Protects extracted metadata using Advanced Encryption Standard for maximum confidentiality."
        },
        {
          title: "Entropy-Based Region Detection",
          desc: "Identifies the busiest image areas using Shannon entropy for optimal data hiding."
        },
        {
          title: "RSA-OAEP Key Exchange",
          desc: "Secures encryption keys with Optimal Asymmetric Encryption Padding."
        },
        {
          title: "LSB Steganography Embedding",
          desc: "Conceals encrypted metadata in image pixels without altering visual quality."
        },
        {
          title: "Argon2 Password Hashing",
          desc: "Strengthens user passwords against brute force and dictionary attacks."
        },
        {
          title: "PSNR & SSIM Quality Metrics",
          desc: "Ensures stego-images maintain high visual fidelity after embedding."
        }
      ].map((item, i) => (
        <div
          key={i}
          className="relative bg-[#1f1f1f] p-6 rounded-lg border text-gray-300
                     before:absolute before:inset-[-1px] before:rounded-lg before:bg-gradient-to-r before:from-[#E04333] before:to-[#6A2F67] before:-z-10
                     shadow-md"
        >
          <h3 className="font-semibold text-[#EC4F2F] mb-2 text-lg">{item.title}</h3>
          <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
        </div>
      ))}
    </div>
  </section>
</FadeInSection>



            {/* Workflow Section */}
            <FadeInSection offset={40} delay={0.2}>
              <section id="workflow" className="py-16 px-6 max-w-6xl mx-auto">
                <h2 className="text-5xl md:text-6xl text-[#EC4F2F] font-bold text-center mb-4 tracking-tight">
                  Learn How It Works
                </h2>
                <p className="text-xl md:text-2xl text-gray-300 text-center mb-12">
                  Military-grade metadata protection through an intuitive, research-backed encryption and steganography workflow.
                </p>

                <div className="grid md:grid-cols-2 gap-10">
                  {/* Encryption Workflow */}
                  <div className="bg-gradient-to-br from-[#2c2c2c]/80 to-[#1a1a1a]/80 backdrop-blur-lg p-10 rounded-2xl border border-gray-700 shadow-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl">
                    <h3 className="font-semibold mb-4 text-3xl md:text-4xl text-[#EC4F2F]">Encryption Workflow</h3>
                    <p className="text-lg md:text-xl text-gray-200 mb-6">
                      Secure your metadata
                    </p>
                    <ul className="list-none space-y-4 text-gray-300 leading-relaxed">
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Initialize ALMV with Argon2-hashed password authentication.
                      </li>
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Upload target images with comprehensive format support.
                      </li>
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Monitor real-time encryption with Shannon entropy analysis.
                      </li>
                    </ul>
                  </div>

                  {/* Decryption Workflow */}
                  <div className="bg-gradient-to-br from-[#2c2c2c]/80 to-[#1a1a1a]/80 backdrop-blur-lg p-10 rounded-2xl border border-gray-700 shadow-2xl transform transition-all duration-300 hover:scale-105 hover:shadow-2xl">
                    <h3 className="font-semibold mb-4 text-3xl md:text-4xl text-[#EC4F2F]">Decryption Workflow</h3>
                    <p className="text-lg md:text-xl text-gray-200 mb-6">
                      Recover your metadata
                    </p>
                    <ul className="list-none space-y-4 text-gray-300 leading-relaxed">
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Authenticate with your secure password for RSA key decryption.
                      </li>
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Load steganographic images for metadata extraction analysis.
                      </li>
                      <li className="flex items-center">
                        <span className="inline-block w-3 h-3 mr-4 rounded-full bg-[#EC4F2F]"></span>
                        Access recovered metadata with full integrity verification.
                      </li>
                    </ul>
                  </div>
                </div>
              </section>
            </FadeInSection>




    {/* Team Section */}
<FadeInSection offset={30} delay={0.3}>
  <section id="team" className="bg-[#121212] py-12 px-8 max-w-6xl mx-auto rounded-lg">
    <h2 className="text-5xl text-[#EC4F2F] font-semibold text-left mb-2 tracking-wide">
      Meet the Team
    </h2>
    <p className="text-2xl text-gray-100 mb-8 leading-snug">
      Meet the researchers and engineers who developed ALMV's state-of-the-art cryptographic and steganographic innovations.
    </p>

    <div className="grid md:grid-cols-4 gap-6">
      {[
        { name: "Angela Samboa", role: "Principal Research • Module Development", img: angelaImg, description: "Leading cryptographic research and core algorithm architecture design." },
        { name: "Licelle Tendilla", role: "User Experience • Quality Assurance", img: licelleImg, description: "Crafting exceptional user experiences and comprehensive system testing." },
        { name: "Mark De Chavez", role: "Module Development • Quality Assurance", img: markImg, description: "Building robust modules and maintaining enterprise-grade code standards." },
        { name: "Vhilly Manalansang", role: "Modules Integration • Deployment", img: vhillyImg, description: "Orchestrating seamless integration and production deployment strategies." },
  
  
      ].map((member, i) => (
        <div
          key={i}
          className="bg-[#1f1f1f]/80 p-5 rounded-xl border border-gray-700 text-center hover:border-red-500 transition-all duration-300 cursor-default shadow-lg hover:shadow-2xl hover:scale-105"
        >
          <div className="mx-auto mb-4 w-38 h-38 rounded-full p-[3px] bg-gradient-to-r from-[#E04333] to-[#6A2F67] shadow-inner">
            <div className="w-full h-full rounded-full overflow-hidden bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
              <img
                src={member.img}
                alt={member.name}
                className="w-full h-full object-cover rounded-full filter grayscale brightness-90 contrast-110 drop-shadow-lg"
              />
            </div>
          </div>

          {/* Member name */}
          <h3 className="font-semibold text-white-400 mb-1 text-lg">{member.name}</h3>

          {/* Role description */}
          <p className="text-xs text-gray-400 mb-2">{member.role}</p>

          <p className="text-gray-300 text-sm leading-snug">{member.description}</p>
        </div>
      ))}
    </div>
  </section>
</FadeInSection>



      {/* Subscribe Section (replaced) */}
      <FadeInSection offset={20} delay={0.4}>
        <SubscribeBlock />
      </FadeInSection>

      {/* Footer */}
      <footer className="bg-[#1D1A13] text-gray-300 py-12 px-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
    <div>

      <div className="flex items-center gap-2">
        <img
          src={ALMV} 
          alt="ALMV Logo"
          className="w-20 h-20"
        />
        <span className="text-4xl font-extrabold bg-gradient-to-r from-[#E04333] to-[#6A2F67] bg-clip-text text-transparent">
          ALMV
        </span>
      </div>

      <p className="text-sm text-white mt-0 mb-3">
        Cryptography + Steganography
      </p>
      <p className="text-sm text-gray-500">
        Pioneering the future of digital privacy through innovative
        cryptographic and steganographic research.
      </p>
    </div>

    {/* Resources */}
    <div>
      <h4 className="font-semibold text-white mb-3">Resources</h4>
      <ul className="space-y-2 text-sm">
        <li><a href="/documentation" className="hover:text-red-500">Documentation</a></li>
        <li><a href="/user-guide" className="hover:text-red-500">User Guide</a></li>
        <li><a href="/api-reference" className="hover:text-red-500">API Reference</a></li>
        <li><a href="https://support.example.com" target="_blank" rel="noopener noreferrer" className="hover:text-red-500">Support Center</a></li>
      </ul>
    </div>

    {/* Research */}
    <div>
      <h4 className="font-semibold text-white mb-3">Research</h4>
      <ul className="space-y-2 text-sm">
        <li><a href="/thesis" className="hover:text-red-500">Thesis Paper</a></li>
        <li><a href="/algorithm-analysis" className="hover:text-red-500">Algorithm Analysis</a></li>
        <li><a href="/security-audit" className="hover:text-red-500">Security Audit</a></li>
        <li><a href="/metrics" className="hover:text-red-500">Performance Metrics</a></li>
      </ul>
    </div>

    {/* Legal */}
    <div>
      <h4 className="font-semibold text-white mb-3">Legal</h4>
      <ul className="space-y-2 text-sm">
        <li><a href="/license" className="hover:text-red-500">License Agreement</a></li>
        <li><a href="/contact" className="hover:text-red-500">Contact</a></li>
      </ul>
    </div>
  </div>

  {/* Bottom note */}
  <div className="max-w-7xl mx-auto mt-8 border-t border-gray-700 pt-4 text-xs text-gray-500 flex justify-between">
    <span>© {new Date().getFullYear()} ALMV. All rights reserved.</span>
    <div className="space-x-4">
      <a href="/terms" className="hover:text-red-500">Terms</a>
      <a href="/privacy" className="hover:text-red-500">Privacy</a>
    </div>
  </div>
</footer>

    </div>
  );
}
