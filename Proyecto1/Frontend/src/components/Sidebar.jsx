import { NavLink } from "react-router-dom";

export default function Sidebar() {
  const base = "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors";
  const active = "bg-slate-700 text-white";
  const inactive = "text-slate-300 hover:bg-slate-700/50 hover:text-white";

  return (
    <aside className="w-64 bg-slate-900 h-screen text-white border-r border-slate-800 p-4 fixed left-0 top-0">
      <div className="mb-6">
        <h1 className="text-lg font-semibold">StudentGuard</h1>
        <p className="text-xs text-slate-400">Panel administrativo</p>
      </div>
      <nav className="space-y-2">
        <NavLink to="/" end className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
          Carga Masiva
        </NavLink>
        <NavLink to="/ajuste" className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
          Ajuste
        </NavLink>
        <NavLink to="/evaluacion" className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
          Evaluación
        </NavLink>
        <NavLink to="/prediccion" className={({ isActive }) => `${base} ${isActive ? active : inactive}`}>
          Predicción
        </NavLink>
      </nav>
    </aside>
  );
}
