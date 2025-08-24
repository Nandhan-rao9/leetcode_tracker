import { Link, NavLink, Outlet } from "react-router-dom";
import "./AppLayout.css"; // optional: create or inline styles

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Link to="/">LC Tracker</Link></div>
        <nav>
          <NavLink to="/revision">Revision</NavLink>
          <NavLink to="/company">Company Prep</NavLink>
        </nav>
      </aside>
      <main className="content">
        <header className="topbar">
          <div />
          <div className="spacer" />
        </header>
        <section className="page">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
