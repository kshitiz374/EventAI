"use client";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  Sparkles, Calendar, DollarSign, Users, BarChart3,
  CheckSquare, Zap, Shield, ArrowRight, Star, 
  Globe, Clock, Wand2, ChevronRight, TrendingUp
} from "lucide-react";

const features = [
  {
    icon: Wand2,
    title: "AI Event Wizard",
    description: "Describe your event in plain language. Get a complete plan with budget, timeline, and personalized recommendations instantly.",
    color: "#6366f1",
  },
  {
    icon: DollarSign,
    title: "Smart Budget Optimizer",
    description: "AI allocates your budget intelligently across categories. Real-time tracking with overrun alerts and cost-saving alternatives.",
    color: "#10b981",
  },
  {
    icon: Calendar,
    title: "AI Timeline Generator",
    description: "Auto-generate preparation schedules with deadlines, dependencies, and priority-based task ordering based on your event date.",
    color: "#f59e0b",
  },
  {
    icon: Sparkles,
    title: "Event Copilot",
    description: "Chat naturally with your AI assistant. Ask anything — budget cuts, theme ideas, vendor tips, or what-if scenarios.",
    color: "#ec4899",
  },
  {
    icon: Users,
    title: "Guest & RSVP Manager",
    description: "Manage your guest list, track RSVPs, dietary needs, and generate personalized invitations for WhatsApp, email, or print.",
    color: "#3b82f6",
  },
  {
    icon: TrendingUp,
    title: "What-If Simulator",
    description: "Test scenarios before committing. See the financial and logistical impact of budget changes, guest count shifts, or date changes.",
    color: "#8b5cf6",
  },
];

const stats = [
  { value: "50+", label: "Event Types Supported" },
  { value: "₹0", label: "Base Cost" },
  { value: "10x", label: "Faster Planning" },
  { value: "AI", label: "Powered Intelligence" },
];

const eventTypes = [
  { emoji: "💍", label: "Weddings" },
  { emoji: "🎂", label: "Birthdays" },
  { emoji: "💻", label: "Hackathons" },
  { emoji: "🏢", label: "Corporate" },
  { emoji: "🎉", label: "Festivals" },
  { emoji: "🤝", label: "Community" },
  { emoji: "💕", label: "Anniversaries" },
  { emoji: "🎓", label: "Graduations" },
];

export default function LandingPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) router.replace("/dashboard");
  }, [user, router]);

  return (
    <div className="hero-bg min-h-screen">
      {/* Navigation */}
      <nav className="glass sticky top-0 z-50 border-b" style={{ borderColor: "var(--border)" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 2rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
              <div style={{
                width: 36, height: 36, borderRadius: 10,
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                display: "flex", alignItems: "center", justifyContent: "center"
              }}>
                <Sparkles size={18} color="white" />
              </div>
              <span style={{ fontFamily: "Outfit, sans-serif", fontWeight: 800, fontSize: "1.25rem" }}>
                Eventra <span className="gradient-text">AI</span>
              </span>
            </div>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Link href="/login" className="btn btn-ghost">Sign In</Link>
              <Link href="/register" className="btn btn-primary">Get Started Free</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "6rem 2rem 4rem" }}>
        <div style={{ textAlign: "center", maxWidth: 820, margin: "0 auto" }}>
          <div className="badge" style={{
            display: "inline-flex", marginBottom: "1.5rem",
            background: "rgba(99,102,241,0.1)", color: "#a78bfa",
            border: "1px solid rgba(99,102,241,0.2)"
          }}>
            <Zap size={12} /> Powered by Advanced AI · Plan Any Event in Minutes
          </div>

          <h1 style={{ fontSize: "clamp(2.5rem, 6vw, 4.5rem)", marginBottom: "1.5rem" }}>
            Plan Your{" "}
            <span className="gradient-text">Perfect Event</span>
            <br />with AI Intelligence
          </h1>

          <p style={{ fontSize: "1.25rem", color: "var(--text-secondary)", maxWidth: 600, margin: "0 auto 2.5rem", lineHeight: 1.7 }}>
            Describe your event. Let Eventra AI build a complete plan — budget, 
            timeline, guest list, vendors, themes, and more. All in one intelligent dashboard.
          </p>

          {/* Demo Prompt */}
          <div className="card" style={{ maxWidth: 680, margin: "0 auto 2rem", padding: "1.25rem 1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981", animation: "pulse-glow 2s infinite" }} />
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9375rem", fontStyle: "italic", flexGrow: 1 }}>
                "Plan a cyberpunk-themed birthday for 50 friends in Patna. Budget ₹25,000, event in 20 days."
              </p>
              <Sparkles size={16} color="#6366f1" />
            </div>
          </div>

          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/register" className="btn btn-primary btn-xl">
              Start Planning Free <ArrowRight size={18} />
            </Link>
            <Link href="/login" className="btn btn-secondary btn-xl">
              View Demo <ChevronRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "2rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
          {stats.map((s) => (
            <div key={s.label} className="card" style={{ textAlign: "center", padding: "1.5rem" }}>
              <div className="stat-number gradient-text">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Event Types */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "4rem 2rem 2rem" }}>
        <h2 style={{ textAlign: "center", fontSize: "1.125rem", color: "var(--text-secondary)", fontWeight: 500, fontFamily: "Inter", marginBottom: "1.5rem" }}>
          Plan any event — from intimate gatherings to grand celebrations
        </h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", justifyContent: "center" }}>
          {eventTypes.map((et) => (
            <div key={et.label} className="badge" style={{
              padding: "0.5rem 1rem", fontSize: "0.875rem",
              background: "var(--bg-card)", border: "1px solid var(--border)",
              color: "var(--text-secondary)"
            }}>
              {et.emoji} {et.label}
            </div>
          ))}
        </div>
      </section>

      {/* Features Grid */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "4rem 2rem" }}>
        <h2 style={{ textAlign: "center", fontSize: "2.5rem", fontFamily: "Outfit, sans-serif", marginBottom: "1rem" }}>
          Everything You Need to Plan a{" "}
          <span className="gradient-text">Flawless Event</span>
        </h2>
        <p style={{ textAlign: "center", color: "var(--text-secondary)", marginBottom: "3rem", fontSize: "1.0625rem" }}>
          One intelligent platform — from first idea to final toast.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "1.5rem" }}>
          {features.map((f) => (
            <div key={f.title} className="feature-card animate-fade-in">
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: `${f.color}15`, border: `1px solid ${f.color}30`,
                display: "flex", alignItems: "center", justifyContent: "center",
                marginBottom: "1.25rem"
              }}>
                <f.icon size={22} color={f.color} />
              </div>
              <h3 style={{ fontSize: "1.125rem", marginBottom: "0.625rem" }}>{f.title}</h3>
              <p style={{ color: "var(--text-secondary)", lineHeight: 1.7, fontSize: "0.9375rem" }}>{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "4rem 2rem" }}>
        <div className="card" style={{ padding: "3rem", background: "linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05))", border: "1px solid rgba(99,102,241,0.2)" }}>
          <h2 style={{ textAlign: "center", fontSize: "2rem", marginBottom: "3rem" }}>
            From Idea to Execution in <span className="gradient-text">3 Simple Steps</span>
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "2rem" }}>
            {[
              { step: "01", title: "Describe Your Event", desc: "Tell the AI about your event type, date, budget, guests, and vibe. Or fill a quick form.", icon: "💬" },
              { step: "02", title: "Get Your AI Plan", desc: "Receive a complete plan: budget breakdown, task timeline, themes, and recommendations.", icon: "✨" },
              { step: "03", title: "Manage Everything", desc: "Track tasks, manage guests, compare vendors, and chat with your AI copilot anytime.", icon: "🚀" },
            ].map((step) => (
              <div key={step.step} style={{ textAlign: "center" }}>
                <div style={{ fontSize: "3rem", marginBottom: "0.75rem" }}>{step.icon}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--accent)", fontWeight: 700, letterSpacing: "0.15em", marginBottom: "0.5rem" }}>STEP {step.step}</div>
                <h3 style={{ fontSize: "1.125rem", marginBottom: "0.625rem" }}>{step.title}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.9375rem", lineHeight: 1.7 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "4rem 2rem 6rem" }}>
        <div style={{ textAlign: "center" }}>
          <h2 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>
            Ready to Plan Your <span className="gradient-text">Dream Event</span>?
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "1.0625rem", marginBottom: "2.5rem" }}>
            Join thousands of event planners who trust Eventra AI for their most important moments.
          </p>
          <Link href="/register" className="btn btn-primary btn-xl animate-pulse-glow">
            <Sparkles size={20} /> Start Planning — It's Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border-subtle)", padding: "2rem", textAlign: "center" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
          <Sparkles size={16} color="#6366f1" />
          <span style={{ fontFamily: "Outfit, sans-serif", fontWeight: 700, color: "var(--text-secondary)" }}>Eventra AI</span>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>
          Intelligent event planning powered by AI. Built with ❤️ for event creators.
        </p>
      </footer>
    </div>
  );
}
