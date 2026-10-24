import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = "INR"): string {
  const symbols: Record<string, string> = {
    INR: "₹",
    USD: "$",
    EUR: "€",
    GBP: "£",
  };
  const symbol = symbols[currency] || currency + " ";
  return `${symbol}${amount.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "Not set";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

export function daysUntil(dateStr: string | null | undefined): number | null {
  if (!dateStr) return null;
  const diff = new Date(dateStr).getTime() - Date.now();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export function getPriorityColor(priority: string): string {
  const map: Record<string, string> = {
    critical: "text-red-400 bg-red-500/10 border-red-500/20",
    high: "text-orange-400 bg-orange-500/10 border-orange-500/20",
    medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
    low: "text-green-400 bg-green-500/10 border-green-500/20",
  };
  return map[priority] || "text-gray-400 bg-gray-500/10";
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    completed: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    in_progress: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    pending: "text-gray-400 bg-gray-500/10 border-gray-500/20",
    overdue: "text-red-400 bg-red-500/10 border-red-500/20",
    confirmed: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    declined: "text-red-400 bg-red-500/10 border-red-500/20",
    invited: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    booked: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    shortlisted: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
    planning: "text-blue-400 bg-blue-500/10",
    draft: "text-gray-400 bg-gray-500/10",
  };
  return map[status] || "text-gray-400 bg-gray-500/10";
}

export function getEventTypeEmoji(eventType: string): string {
  const map: Record<string, string> = {
    wedding: "💍",
    birthday: "🎂",
    anniversary: "💕",
    festival: "🎉",
    hackathon: "💻",
    corporate: "🏢",
    community: "🤝",
    other: "🎊",
  };
  return map[eventType] || "🎊";
}
