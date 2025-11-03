import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
export function AppLayout() {
    var logout = useAuth().logout;
    return (_jsxs("div", { className: "layout", children: [_jsxs("aside", { className: "sidebar", children: [_jsx("div", { className: "logo", children: "Clipador" }), _jsxs("nav", { children: [_jsx(NavLink, { to: "/", end: true, className: function (_a) {
                                    var isActive = _a.isActive;
                                    return (isActive ? "active" : undefined);
                                }, children: "Dashboard" }), _jsx(NavLink, { to: "/streams", className: function (_a) {
                                    var isActive = _a.isActive;
                                    return (isActive ? "active" : undefined);
                                }, children: "Streams" })] }), _jsx("button", { type: "button", onClick: function () { return void logout(); }, className: "logout-button", children: "Sair" })] }), _jsx("main", { className: "content", children: _jsx(Outlet, {}) })] }));
}
