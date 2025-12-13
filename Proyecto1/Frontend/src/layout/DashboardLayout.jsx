import Sidebar from "../components/Sidebar.jsx";
import { Outlet } from "react-router-dom";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-slate-950">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 overflow-auto">
        <div className="min-h-full bg-slate-900/40 rounded-xl border border-slate-800 p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
