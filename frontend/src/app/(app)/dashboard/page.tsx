"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { aiApi, eventsApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { formatCurrency, formatDate, daysUntil, getEventTypeEmoji, getStatusColor } from "@/lib/utils";
import {
  Calendar, DollarSign, CheckSquare, Users, Plus,
  TrendingUp, AlertTriangle, Sparkles, ArrowRight,
  Clock, Target, Zap
} from "lucide-react";

interface DashboardStats {
  total_events: number;
  upcoming_events: number;
  total_budget: number;
  pending_tasks: number;
  overdue_tasks: number;
  total_guests: number;
  confirmed_guests: number;
  upcoming_events_list: any[];
}

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await aiApi.dashboardStats();
        setStats(res.data);
      } catch (e: any) {
        setError("Could not load dashboard. Is the backend running?");
      } finally { setLoading(false); }
    })();
  }, []);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh" }}>
        <div style={{ textAlign: "center" }}>
          <div className="spinner" style={{ width: 40, height: 40, margin: "0 auto 1rem" }} />
          <p style={{ color: "var(--text-secondary)" }}>Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <div style={{ fontSize: "3rem" }}>⚠️</div>
        <h2>Backend not connected</h2>
        <p style={{ maxWidth: 400 }}>{error}</p>
        <div style={{ background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)", borderRadius: 8, padding: "1rem 1.5rem", marginTop: "0.5rem", fontSize: "0.875rem", color: "var(--text-secondary)", textAlign: "left", maxWidth: 420 }}>
          <p style={{ fontWeight: 600, color: "var(--accent)", marginBottom: "0.5rem" }}>Start the backend:</p>
          <code style={{ fontFamily: "monospace", display: "block" }}>cd backend</code>
          <code style={{ fontFamily: "monospace", display: "block" }}>.\venv\Scripts\uvicorn app.main:app --reload</code>
        </div>
      </div>
    );
  }

  const statCards = [
    { label: "Total Events", value: stats?.total_events ?? 0, icon: Calendar, color: "#6366f1", sub: `${stats?.upcoming_events ?? 0} upcoming` },
    { label: "Total Budget", value: formatCurrency(stats?.total_budget ?? 0), icon: DollarSign, color: "#10b981", sub: "across all events" },
    { label: "Pending Tasks", value: stats?.pending_tasks ?? 0, icon: CheckSquare, color: "#f59e0b", sub: stats?.overdue_tasks ? `${stats.overdue_tasks} overdue` : "on track" },
    { label: "Total Guests", value: stats?.total_guests ?? 0, icon: Users, color: "#ec4899", sub: `${stats?.confirmed_guests ?? 0} confirmed` },
  ];

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 17 ? "afternoon" : "evening"},{" "}
            <span className="gradient-text">{user?.full_name.split(" ")[0]}</span> 👋
          </h1>
          <p className="page-subtitle">Here's what's happening with your events today.</p>
        </div>
        <Link href="/events/new" className="btn btn-primary">
          <Plus size={16} /> New Event
        </Link>
      </div>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        {statCards.map((card) => (
          <div key={card.label} className="stat-card">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span className="stat-label">{card.label}</span>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: `${card.color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <card.icon size={18} color={card.color} />
              </div>
            </div>
            <div className="stat-number" style={{ color: card.color }}>{card.value}</div>
            <p style={{ fontSize: "0.75rem", color: stats?.overdue_tasks && card.label === "Pending Tasks" ? "#ef4444" : "var(--text-muted)" }}>
              {card.sub}
            </p>
          </div>
        ))}
      </div>

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "1.5rem", alignItems: "start" }}>
        {/* Upcoming Events */}
        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <h2 style={{ fontSize: "1.125rem" }}>Upcoming Events</h2>
            <Link href="/events" style={{ color: "var(--accent)", fontSize: "0.875rem", fontWeight: 500, textDecoration: "none", display: "flex", alignItems: "center", gap: "0.25rem" }}>
              View all <ArrowRight size={14} />
            </Link>
          </div>

          {(stats?.upcoming_events_list?.length ?? 0) === 0 ? (
            <div className="card" style={{ padding: "3rem", textAlign: "center" }}>
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🎉</div>
              <h3 style={{ marginBottom: "0.5rem" }}>No upcoming events yet</h3>
              <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem" }}>Create your first event and let AI plan it for you.</p>
              <Link href="/events/new" className="btn btn-primary">
                <Plus size={16} /> Plan Your First Event
              </Link>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {stats?.upcoming_events_list.map((event: any) => {
                const days = daysUntil(event.event_date);
                return (
                  <Link key={event.id} href={`/events/${event.id}/overview`} style={{ textDecoration: "none" }}>
                    <div className="card" style={{ padding: "1.25rem", cursor: "pointer" }}>
                      <div style={{ display: "flex", alignItems: "flex-start", gap: "1rem" }}>
                        <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--bg-secondary)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", flexShrink: 0 }}>
                          {getEventTypeEmoji(event.event_type)}
                        </div>
                        <div style={{ flexGrow: 1, minWidth: 0 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", marginBottom: "0.25rem" }}>
                            <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>{event.name}</h3>
                            <span className={`badge ${getStatusColor(event.status)}`}>{event.status}</span>
                          </div>
                          <div style={{ display: "flex", gap: "1rem", color: "var(--text-secondary)", fontSize: "0.8125rem" }}>
                            <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                              <Calendar size={12} /> {formatDate(event.event_date)}
                            </span>
                            {event.location && <span>📍 {event.location}</span>}
                            <span style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
                              <DollarSign size={12} /> {formatCurrency(event.total_budget, event.currency)}
                            </span>
                          </div>
                        </div>
                        {days !== null && (
                          <div style={{ textAlign: "center", flexShrink: 0 }}>
                            <div style={{ fontSize: "1.5rem", fontWeight: 700, fontFamily: "Outfit, sans-serif", color: days <= 7 ? "#ef4444" : days <= 30 ? "#f59e0b" : "var(--accent)" }}>
                              {days}
                            </div>
                            <div style={{ fontSize: "0.6875rem", color: "var(--text-muted)" }}>days left</div>
                          </div>
                        )}
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>

        {/* Right column */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Quick Actions */}
          <div className="card-subtle">
            <h3 style={{ fontSize: "0.9375rem", marginBottom: "0.875rem" }}>Quick Actions</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {[
                { href: "/events/new", icon: Plus, label: "Create new event", color: "#6366f1" },
                { href: "/copilot", icon: Sparkles, label: "Chat with AI Copilot", color: "#ec4899" },
                { href: "/events", icon: Calendar, label: "View all events", color: "#f59e0b" },
              ].map((action) => (
                <Link key={action.href} href={action.href} style={{ textDecoration: "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.625rem 0.75rem", borderRadius: 8, cursor: "pointer", transition: "background 0.15s" }}
                    onMouseEnter={e => (e.currentTarget.style.background = "var(--bg-card-hover)")}
                    onMouseLeave={e => (e.currentTarget.style.background = "transparent")}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: `${action.color}15`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <action.icon size={15} color={action.color} />
                    </div>
                    <span style={{ fontSize: "0.875rem", color: "var(--text-primary)" }}>{action.label}</span>
                    <ArrowRight size={14} color="var(--text-muted)" style={{ marginLeft: "auto" }} />
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* AI Tip Card */}
          <div style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.08))", border: "1px solid rgba(99,102,241,0.2)", borderRadius: "var(--radius)", padding: "1.25rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <Sparkles size={16} color="#a78bfa" />
              <span style={{ fontSize: "0.8125rem", fontWeight: 600, color: "#a78bfa" }}>AI Insight</span>
            </div>
            <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.6 }}>
              {stats?.overdue_tasks && stats.overdue_tasks > 0
                ? `⚠️ You have ${stats.overdue_tasks} overdue task${stats.overdue_tasks > 1 ? "s" : ""}. Open an event to reschedule them.`
                : stats?.pending_tasks
                  ? `📋 ${stats.pending_tasks} tasks are pending across your events. Stay on track to ensure a smooth event day.`
                  : "✨ You're all caught up! Create a new event or chat with the AI Copilot for planning inspiration."}
            </p>
          </div>

          {/* Guest Progress */}
          {(stats?.total_guests ?? 0) > 0 && (
            <div className="card-subtle">
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.875rem" }}>
                <h3 style={{ fontSize: "0.9375rem" }}>Guest Confirmations</h3>
                <span style={{ fontSize: "0.8125rem", color: "var(--text-secondary)" }}>
                  {stats?.confirmed_guests}/{stats?.total_guests}
                </span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${((stats?.confirmed_guests ?? 0) / (stats?.total_guests ?? 1)) * 100}%` }} />
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.5rem" }}>
                {Math.round(((stats?.confirmed_guests ?? 0) / (stats?.total_guests ?? 1)) * 100)}% confirmed
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
