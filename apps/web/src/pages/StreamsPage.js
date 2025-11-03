var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
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
import { useEffect, useState } from "react";
import { attachChannelStreamer, detachChannelStreamer, fetchChannelConfig, fetchDeliveryHistory, } from "../api";
import { useAuth } from "../context/AuthContext";
export function StreamsPage() {
    var _this = this;
    var token = useAuth().token;
    var _a = useState(null), config = _a[0], setConfig = _a[1];
    var _b = useState([]), history = _b[0], setHistory = _b[1];
    var _c = useState(false), loading = _c[0], setLoading = _c[1];
    var _d = useState(null), error = _d[0], setError = _d[1];
    var _e = useState({
        twitch_user_id: "",
        display_name: "",
        avatar_url: "",
        monitor_interval_seconds: 180,
        monitor_min_clips: 2,
    }), form = _e[0], setForm = _e[1];
    useEffect(function () {
        if (!token)
            return;
        function load() {
            return __awaiter(this, void 0, void 0, function () {
                var _a, cfg, deliveries, err_1;
                return __generator(this, function (_b) {
                    switch (_b.label) {
                        case 0:
                            _b.trys.push([0, 2, 3, 4]);
                            setLoading(true);
                            setError(null);
                            return [4 /*yield*/, Promise.all([
                                    fetchChannelConfig(token),
                                    fetchDeliveryHistory(token, 25),
                                ])];
                        case 1:
                            _a = _b.sent(), cfg = _a[0], deliveries = _a[1];
                            setConfig(cfg);
                            setHistory(deliveries.items);
                            return [3 /*break*/, 4];
                        case 2:
                            err_1 = _b.sent();
                            setError(err_1 instanceof Error ? err_1.message : "Erro ao carregar dados");
                            return [3 /*break*/, 4];
                        case 3:
                            setLoading(false);
                            return [7 /*endfinally*/];
                        case 4: return [2 /*return*/];
                    }
                });
            });
        }
        load();
    }, [token]);
    function handleSubmit(event) {
        return __awaiter(this, void 0, void 0, function () {
            var updated, err_2;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        event.preventDefault();
                        if (!token)
                            return [2 /*return*/];
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, 4, 5]);
                        setLoading(true);
                        setError(null);
                        return [4 /*yield*/, attachChannelStreamer(token, {
                                twitch_user_id: form.twitch_user_id,
                                display_name: form.display_name,
                                avatar_url: form.avatar_url || undefined,
                                monitor_interval_seconds: form.monitor_interval_seconds,
                                monitor_min_clips: form.monitor_min_clips,
                            })];
                    case 2:
                        updated = _a.sent();
                        setConfig(updated);
                        setForm({
                            twitch_user_id: "",
                            display_name: "",
                            avatar_url: "",
                            monitor_interval_seconds: 180,
                            monitor_min_clips: 2,
                        });
                        return [3 /*break*/, 5];
                    case 3:
                        err_2 = _a.sent();
                        setError(err_2 instanceof Error ? err_2.message : "Erro ao adicionar streamer");
                        return [3 /*break*/, 5];
                    case 4:
                        setLoading(false);
                        return [7 /*endfinally*/];
                    case 5: return [2 /*return*/];
                }
            });
        });
    }
    return (_jsxs("div", { className: "streams-page", children: [_jsxs("header", { children: [_jsx("h1", { children: "Streams Monitoradas" }), error && _jsx("p", { className: "error", children: error }), config && (_jsxs("div", { className: "plan-summary", children: [_jsxs("span", { children: ["Slots: ", config.slots_used, "/", config.slots_total, " (base ", config.slots_base, ")"] }), _jsxs("span", { children: ["Modo: ", config.monitor_mode] })] }))] }), _jsx("section", { className: "stream-form-wrapper", children: _jsxs("form", { className: "stream-form", onSubmit: handleSubmit, children: [_jsxs("div", { className: "form-grid", children: [_jsxs("label", { children: ["Twitch User ID", _jsx("input", { value: form.twitch_user_id, onChange: function (e) { return setForm(function (prev) { return (__assign(__assign({}, prev), { twitch_user_id: e.target.value })); }); }, required: true })] }), _jsxs("label", { children: ["Nome exibido", _jsx("input", { value: form.display_name, onChange: function (e) { return setForm(function (prev) { return (__assign(__assign({}, prev), { display_name: e.target.value })); }); }, required: true })] }), _jsxs("label", { children: ["Avatar URL", _jsx("input", { value: form.avatar_url, onChange: function (e) { return setForm(function (prev) { return (__assign(__assign({}, prev), { avatar_url: e.target.value })); }); } })] }), _jsxs("label", { children: ["Intervalo (segundos)", _jsx("input", { type: "number", min: 30, value: form.monitor_interval_seconds, onChange: function (e) {
                                                return setForm(function (prev) { return (__assign(__assign({}, prev), { monitor_interval_seconds: Number(e.target.value) })); });
                                            } })] }), _jsxs("label", { children: ["M\u00EDnimo de clipes", _jsx("input", { type: "number", min: 1, value: form.monitor_min_clips, onChange: function (e) {
                                                return setForm(function (prev) { return (__assign(__assign({}, prev), { monitor_min_clips: Number(e.target.value) })); });
                                            } })] })] }), _jsx("button", { type: "submit", disabled: loading, children: loading ? "Salvando..." : "Adicionar streamer" })] }) }), _jsxs("section", { className: "stream-list", children: [config === null || config === void 0 ? void 0 : config.streamers.map(function (stream) {
                        var _a;
                        return (_jsxs("article", { className: "stream-card", children: [_jsxs("div", { children: [_jsx("h2", { children: stream.display_name }), _jsxs("p", { children: ["ID Twitch: ", stream.twitch_user_id] }), stream.label && _jsxs("p", { children: ["Etiqueta: ", stream.label] }), ((_a = stream.status) === null || _a === void 0 ? void 0 : _a.status) && _jsxs("p", { children: ["Status: ", stream.status.status] })] }), _jsxs("div", { className: "stream-meta", children: [_jsxs("span", { children: ["Intervalo: ", stream.monitor_interval_seconds, "s"] }), _jsxs("span", { children: ["M\u00EDnimo: ", stream.monitor_min_clips] }), _jsx("button", { type: "button", onClick: function () { return __awaiter(_this, void 0, void 0, function () {
                                                var updated, err_3;
                                                return __generator(this, function (_a) {
                                                    switch (_a.label) {
                                                        case 0:
                                                            if (!token)
                                                                return [2 /*return*/];
                                                            _a.label = 1;
                                                        case 1:
                                                            _a.trys.push([1, 3, , 4]);
                                                            return [4 /*yield*/, detachChannelStreamer(token, stream.streamer_id)];
                                                        case 2:
                                                            updated = _a.sent();
                                                            setConfig(updated);
                                                            return [3 /*break*/, 4];
                                                        case 3:
                                                            err_3 = _a.sent();
                                                            setError(err_3 instanceof Error ? err_3.message : "Erro ao remover streamer");
                                                            return [3 /*break*/, 4];
                                                        case 4: return [2 /*return*/];
                                                    }
                                                });
                                            }); }, children: "Remover" })] })] }, stream.id));
                    }), (config === null || config === void 0 ? void 0 : config.streamers.length) === 0 && !loading && _jsx("p", { children: "Nenhum streamer cadastrado ainda." })] }), _jsxs("section", { className: "history-list", children: [_jsx("h2", { children: "Hist\u00F3rico recente" }), history.length === 0 && _jsx("p", { children: "Sem entregas registradas." }), history.map(function (item) {
                        var _a;
                        return (_jsxs("article", { children: [_jsxs("div", { className: "history-entry", children: [_jsx("strong", { children: item.streamer_display_name }), _jsx("span", { children: new Date(item.delivered_at).toLocaleString() })] }), _jsxs("p", { children: ["Clip: ", (_a = item.clip_external_id) !== null && _a !== void 0 ? _a : "N/A"] }), item.clip_title && _jsxs("p", { children: ["T\u00EDtulo: ", item.clip_title] }), typeof item.viewer_count === "number" && _jsxs("p", { children: ["Views: ", item.viewer_count] })] }, "".concat(item.streamer_twitch_id, "-").concat(item.delivered_at, "-").concat(item.clip_external_id || "")));
                    })] })] }));
}
