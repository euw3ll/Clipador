import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function AppLayout() {
  const { logout } = useAuth();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">Clipador</div>
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : undefined)}>
            Dashboard
          </NavLink>
          <NavLink to="/streams" className={({ isActive }) => (isActive ? "active" : undefined)}>
            Streams
          </NavLink>
        </nav>
        <button type="button" onClick={() => void logout()} className="logout-button">
          Sair
        </button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
