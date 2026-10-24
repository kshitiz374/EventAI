"use client";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Sparkles, Mail, Lock, User, Eye, EyeOff, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) { setError("Passwords do not match"); return; }
    if (form.password.length < 6) { setError("Password must be at least 6 characters"); return; }
    setLoading(true);
    try {
      await register(form.email, form.full_name, form.password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg-primary)", padding: "1rem" }}
      className="hero-bg">
      <div style={{ width: "100%", maxWidth: 440 }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <Link href="/" style={{ display: "inline-flex", alignItems: "center", gap: "0.625rem", textDecoration: "none" }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: "linear-gradient(135deg, #6366f1, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Sparkles size={20} color="white" />
            </div>
            <span style={{ fontFamily: "Outfit, sans-serif", fontWeight: 800, fontSize: "1.5rem" }}>
              Eventra <span className="gradient-text">AI</span>
            </span>
          </Link>
          <h1 style={{ fontSize: "1.75rem", marginTop: "1.5rem", marginBottom: "0.5rem" }}>Create your account</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9375rem" }}>Start planning amazing events with AI</p>
        </div>

        <div className="card" style={{ padding: "2rem" }}>
          {error && (
            <div style={{ display: "flex", gap: "0.625rem", padding: "0.75rem 1rem", borderRadius: 8, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", color: "#ef4444", marginBottom: "1.25rem", fontSize: "0.875rem" }}>
              <AlertCircle size={16} style={{ flexShrink: 0, marginTop: 1 }} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="label">Full Name</label>
              <div style={{ position: "relative" }}>
                <User size={16} style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input id="reg-name" className="input" type="text" placeholder="Jane Doe" required
                  value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })}
                  style={{ paddingLeft: "2.25rem" }} />
              </div>
            </div>

            <div className="form-group">
              <label className="label">Email</label>
              <div style={{ position: "relative" }}>
                <Mail size={16} style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input id="reg-email" className="input" type="email" placeholder="jane@example.com" required
                  value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
                  style={{ paddingLeft: "2.25rem" }} />
              </div>
            </div>

            <div className="form-group">
              <label className="label">Password</label>
              <div style={{ position: "relative" }}>
                <Lock size={16} style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input id="reg-pass" className="input" type={showPass ? "text" : "password"} placeholder="Min 6 characters" required
                  value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
                  style={{ paddingLeft: "2.25rem", paddingRight: "2.5rem" }} />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  style={{ position: "absolute", right: "0.75rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)" }}>
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div className="form-group">
              <label className="label">Confirm Password</label>
              <div style={{ position: "relative" }}>
                <Lock size={16} style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                <input id="reg-confirm" className="input" type={showPass ? "text" : "password"} placeholder="Repeat password" required
                  value={form.confirm} onChange={e => setForm({ ...form, confirm: e.target.value })}
                  style={{ paddingLeft: "2.25rem" }} />
              </div>
            </div>

            <button id="reg-submit" type="submit" className="btn btn-primary btn-lg" style={{ width: "100%", marginTop: "0.5rem" }} disabled={loading}>
              {loading ? <><div className="spinner" style={{ width: 16, height: 16 }} /> Creating account…</> : "Create Account"}
            </button>
          </form>
        </div>

        <p style={{ textAlign: "center", marginTop: "1.5rem", color: "var(--text-secondary)", fontSize: "0.9375rem" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--accent)", fontWeight: 600, textDecoration: "none" }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
