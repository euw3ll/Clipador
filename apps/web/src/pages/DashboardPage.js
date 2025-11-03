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
import { useEffect, useMemo, useState } from "react";
import { fetchRecentBursts, resolveMonitoring } from "../api";
import { useAuth } from "../context/AuthContext";
export function DashboardPage() {
    var token = useAuth().token;
    var _a = useState([]), bursts = _a[0], setBursts = _a[1];
    var _b = useState(null), monitoring = _b[0], setMonitoring = _b[1];
    var _c = useState("idle"), status = _c[0], setStatus = _c[1];
    var _d = useState(null), error = _d[0], setError = _d[1];
    useEffect(function () {
        if (!token) {
            return;
        }
        var active = true;
        function load() {
            return __awaiter(this, void 0, void 0, function () {
                var _a, burstsData, monitoringData, err_1;
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            setStatus("loading");
                            setError(null);
                            _b.label = 1;
                        case 1:
                            _b.trys.push([1, 3, , 4]);
                            return [4 /*yield*/, Promise.all([
                                    fetchRecentBursts(token),
                                    resolveMonitoring(token),
                                ])];
                        case 2:
                            _a = _b.sent(), burstsData = _a[0], monitoringData = _a[1];
                            if (!active)
                                return [2 /*return*/];
                            setBursts(burstsData);
                            setMonitoring(monitoringData);
                            setStatus("success");
                            return [3 /*break*/, 4];
                        case 3:
                            err_1 = _b.sent();
                            if (!active)
                                return [2 /*return*/];
                            setError(err_1 instanceof Error ? err_1.message : "Erro ao carregar dados");
                            setStatus("error");
                            return [3 /*break*/, 4];
                        case 4: return [2 /*return*/];
                    }
                });
            });
        }
        load();
        var timer = window.setInterval(load, 60000);
        return function () {
            active = false;
            window.clearInterval(timer);
        };
    }, [token]);
    var headline = useMemo(function () {
        if (status === "loading")
            return "Carregando bursts...";
        if (status === "error")
            return "Ocorreu um erro";
        if (bursts.length === 0)
            return "Nenhum burst recente";
        return "Bursts recentes (".concat(bursts.length, ")");
    }, [status, bursts.length]);
    return (_jsxs("div", { className: "dashboard", children: [_jsxs("header", { className: "dashboard-header", children: [_jsx("h1", { children: "Dashboard" }), _jsx("p", { children: headline }), monitoring && (_jsxs("div", { className: "monitoring-card", children: [_jsx("span", { children: "Preset atual" }), _jsxs("strong", { children: [monitoring.intervalo_segundos, "s"] }), _jsxs("span", { children: ["M\u00EDnimo ", monitoring.min_clipes, " clipes"] })] })), error && _jsx("p", { className: "error", children: error })] }), _jsx("section", { className: "burst-list", children: bursts.map(function (burst) { return (_jsxs("article", { className: "burst-card", children: [_jsx("h2", { children: new Date(burst.inicio_iso).toLocaleString() }), _jsxs("p", { children: [burst.clipes.length, " clipes agrupados"] }), _jsx("ul", { children: burst.clipes.map(function (clip) { return (_jsxs("li", { children: [_jsxs("div", { children: [_jsxs("span", { className: "clip-id", children: ["Clip ", clip.id.toUpperCase()] }), _jsx("span", { className: "clip-time", children: new Date(clip.created_at).toLocaleTimeString() })] }), _jsxs("div", { children: [_jsxs("span", { children: [clip.viewer_count, " viewers"] }), clip.streamer_name && _jsx("span", { children: clip.streamer_name })] })] }, clip.id)); }) })] }, "".concat(burst.inicio_iso, "-").concat(burst.fim))); }) })] }));
}
