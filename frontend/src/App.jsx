import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import ProjectView from "./pages/ProjectView.jsx";
import Retrospective from "./pages/Retrospective.jsx";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/retrospective", label: "Retrospective" }
];

export default function App() {
  return (
    <div className="app-shell">
      <div className="glow" aria-hidden="true" />
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">DG</div>
          <div>
            <div className="brand-title">Daily Goals</div>
            <div className="brand-sub">Momentum with clarity</div>
          </div>
        </div>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:projectId" element={<ProjectView />} />
          <Route path="/retrospective" element={<Retrospective />} />
        </Routes>
      </main>
    </div>
  );
}
