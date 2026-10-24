"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";
import {
  Sparkles, LayoutDashboard, Calendar, DollarSign,
  CheckSquare, Users, Truck, MessageSquare, Palette,
  GitBranch, Settings, LogOut, Menu, X, ChevronRight, Plus
} from "lucide-react";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/events", icon: Calendar, label: "My Events" },
  { href: "/copilot", icon: MessageSquare, label: "AI Copilot" },
];

const eventNavItems = [
  { href: "overview", icon: Calendar, label: "Overview" },
  { href: "budget", icon: DollarSign, label: "Budget" },
  { href: "tasks", icon: CheckSquare, label: "Timeline & Tasks" },
  { href: "guests", icon: Users, label: "Guests" },
  { href: "vendors", icon: Truck, label: "Vendors" },
  { href: "copilot", icon: MessageSquare, label: "Event Copilot" },
  { href: "studio", icon: Palette, label: "Creative Studio" },
  { href: "simulator", icon: GitBranch, label: "What-If Simulator" },
];

interface SidebarProps {
  eventId?: string;
}

export function Sidebar({ eventId }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className="sidebar" style={{ width: collapsed ? 64 : 256, transition: "width 0.25s ease" }}>
      {/* Logo */}
      <div style={{ padding: collapsed ? "1.25rem 1rem" : "1.25rem 1.25rem", borderBottom: "1px solid var(--border-subtle)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        {!collapsed && (
          <Link href="/dashboard" style={{ display: "flex", alignItems: "center", gap: "0.5rem", textDecoration: "none" }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #6366f1, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Sparkles size={15} color="white" />
            </div>
            <span style={{ fontFamily: "Outfit, sans-serif", fontWeight: 800, fontSize: "1.0625rem" }}>
              Eventra <span className="gradient-text">AI</span>
            </span>
          </Link>
        )}
        <button onClick={() => setCollapsed(!collapsed)} className="btn btn-ghost btn-sm" style={{ padding: "0.375rem" }}>
          {collapsed ? <ChevronRight size={16} /> : <Menu size={16} />}
        </button>
      </div>

      {/* Main nav */}
      <div style={{ padding: "0.75rem 0.75rem", flexGrow: 1, overflowY: "auto" }}>
        {/* Create event button */}
        {!collapsed && (
          <Link href="/events/new" style={{ textDecoration: "none" }}>
            <div style={{
              display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.5rem 0.875rem",
              borderRadius: 8, background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              color: "white", fontSize: "0.8125rem", fontWeight: 600, cursor: "pointer",
              marginBottom: "1rem", boxShadow: "0 2px 10px rgba(99,102,241,0.3)"
            }}>
              <Plus size={14} /> New Event
            </div>
          </Link>
        )}

        <div style={{ marginBottom: "0.25rem", paddingLeft: collapsed ? 0 : "0.5rem" }}>
          {!collapsed && <p style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>Main</p>}
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className={`sidebar-nav-item ${active ? "active" : ""}`} style={{ justifyContent: collapsed ? "center" : undefined }}>
                <item.icon size={17} />
                {!collapsed && item.label}
              </Link>
            );
          })}
        </div>

        {/* Event-specific nav */}
        {eventId && !collapsed && (
          <div style={{ marginTop: "1.25rem" }}>
            <p style={{ fontSize: "0.6875rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem", paddingLeft: "0.5rem" }}>This Event</p>
            {eventNavItems.map((item) => {
              const href = `/events/${eventId}/${item.href}`;
              const active = pathname === href || pathname.startsWith(href);
              return (
                <Link key={item.href} href={href} className={`sidebar-nav-item ${active ? "active" : ""}`}>
                  <item.icon size={16} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        )}
      </div>

      {/* User section */}
      <div style={{ padding: "0.75rem", borderTop: "1px solid var(--border-subtle)" }}>
        <Link href="/settings" className="sidebar-nav-item" style={{ justifyContent: collapsed ? "center" : undefined }}>
          <Settings size={16} />
          {!collapsed && "Settings"}
        </Link>
        <button onClick={logout} className="sidebar-nav-item btn-danger" style={{
          width: "100%", border: "none", background: "transparent",
          justifyContent: collapsed ? "center" : undefined,
          color: "var(--text-secondary)", fontSize: "0.875rem"
        }}>
          <LogOut size={16} />
          {!collapsed && "Sign out"}
        </button>

        {!collapsed && user && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", padding: "0.75rem 0.5rem 0.25rem", marginTop: "0.25rem" }}>
            <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8125rem", fontWeight: 700, color: "white", flexShrink: 0 }}>
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div style={{ minWidth: 0 }}>
              <p style={{ fontSize: "0.8125rem", fontWeight: 600, truncate: "truncate", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.full_name}</p>
              <p style={{ fontSize: "0.6875rem", color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user.email}</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
