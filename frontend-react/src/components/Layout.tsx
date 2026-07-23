import { ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Phone,
  Users,
  Megaphone,
  History,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

interface NavItem {
  label: string;
  path: string;
  icon: ReactNode;
}

const navItems: NavItem[] = [
  { label: "Dashboard", path: "/", icon: <Phone size={20} /> },
  { label: "Leads", path: "/leads", icon: <Users size={20} /> },
  { label: "Campaigns", path: "/campaigns", icon: <Megaphone size={20} /> },
  { label: "Call History", path: "/call-history", icon: <History size={20} /> },
  { label: "Settings", path: "/settings", icon: <Settings size={20} /> },
];

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isActive = (path: string) => {
    if (path === "/") return location.pathname === "/";
    return location.pathname.startsWith(path);
  };

  const handleSignOut = () => {
    logout();
    navigate("/login");
  };

  const initials = user
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <aside className="fixed left-0 top-0 z-40 flex h-screen w-[280px] flex-col bg-gradient-to-b from-[#0F172A] to-[#1E293B] text-white">
        <div className="flex items-center gap-3 px-6 pt-8 pb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600">
            <Phone size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">AI Cold Calling</h1>
            <p className="text-xs text-blue-300">Health Insurance Agent</p>
          </div>
        </div>

        {user && (
          <div className="mx-4 mb-6 flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-4 py-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-500 text-sm font-semibold">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.full_name}</p>
              <p className="text-xs text-blue-300 truncate capitalize">{user.role}</p>
            </div>
          </div>
        )}

        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => {
            const active = isActive(item.path);
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-150 ${
                  active
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                    : "text-gray-300 hover:bg-white/10 hover:text-white"
                }`}
              >
                <span className={active ? "text-white" : "text-gray-400"}>
                  {item.icon}
                </span>
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t border-white/10">
          <div className="mb-3 flex items-center gap-2 rounded-lg bg-emerald-500/10 px-3 py-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
            </span>
            <span className="text-xs font-medium text-emerald-400">
              System Online
            </span>
          </div>
          <button
            onClick={handleSignOut}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-sm font-medium text-gray-400 transition-colors hover:bg-red-500/10 hover:text-red-400"
          >
            <LogOut size={20} />
            Sign Out
          </button>
        </div>
      </aside>

      <main className="ml-[280px] flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}
