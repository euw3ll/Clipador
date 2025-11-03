var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
export function LoginPage() {
    var _a = useAuth(), login = _a.login, loading = _a.loading, error = _a.error;
    var navigate = useNavigate();
    var location = useLocation();
    var _b = useState(""), username = _b[0], setUsername = _b[1];
    var _c = useState(""), password = _c[0], setPassword = _c[1];
    function handleSubmit(event) {
        return __awaiter(this, void 0, void 0, function () {
            var ok, redirect;
            var _a, _b, _c;
            return __generator(this, function (_d) {
                switch (_d.label) {
                    case 0:
                        event.preventDefault();
                        return [4 /*yield*/, login(username, password)];
                    case 1:
                        ok = _d.sent();
                        if (ok) {
                            redirect = (_c = (_b = (_a = location.state) === null || _a === void 0 ? void 0 : _a.from) === null || _b === void 0 ? void 0 : _b.pathname) !== null && _c !== void 0 ? _c : "/";
                            navigate(redirect, { replace: true });
                        }
                        return [2 /*return*/];
                }
            });
        });
    }
    return (_jsx("div", { className: "auth-wrapper", children: _jsxs("form", { className: "auth-card", onSubmit: handleSubmit, children: [_jsx("h1", { children: "Entrar" }), _jsxs("label", { children: ["Usu\u00E1rio", _jsx("input", { type: "text", value: username, onChange: function (e) { return setUsername(e.target.value); }, placeholder: "admin", autoComplete: "username", required: true })] }), _jsxs("label", { children: ["Senha", _jsx("input", { type: "password", value: password, onChange: function (e) { return setPassword(e.target.value); }, placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022", autoComplete: "current-password", required: true })] }), error && _jsx("p", { className: "auth-error", children: error }), _jsx("button", { type: "submit", disabled: loading, children: loading ? "Entrando..." : "Entrar" })] }) }));
}
