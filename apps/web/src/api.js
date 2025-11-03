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
var _a;
var API_BASE_URL = (_a = import.meta.env.VITE_API_BASE_URL) !== null && _a !== void 0 ? _a : "http://localhost:8000";
function buildHeaders(token, additional) {
    if (additional === void 0) { additional = {}; }
    var headers = __assign({ Accept: "application/json" }, additional);
    if (token) {
        headers["Authorization"] = "Bearer ".concat(token);
    }
    return headers;
}
export function loginRequest(username, password) {
    return __awaiter(this, void 0, void 0, function () {
        var url, response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    url = new URL("/auth/login", API_BASE_URL);
                    return [4 /*yield*/, fetch(url, {
                            method: "POST",
                            headers: buildHeaders(null, { "Content-Type": "application/json" }),
                            body: JSON.stringify({ username: username, password: password }),
                        })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Credenciais inválidas");
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function fetchRecentBursts(token_1) {
    return __awaiter(this, arguments, void 0, function (token, sinceMinutes) {
        var url, response, body;
        if (sinceMinutes === void 0) { sinceMinutes = 60; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    url = new URL("/clips/bursts/recent", API_BASE_URL);
                    url.searchParams.set("since_minutes", String(sinceMinutes));
                    return [4 /*yield*/, fetch(url, {
                            headers: buildHeaders(token),
                        })];
                case 1:
                    response = _a.sent();
                    if (!response.ok) {
                        throw new Error("Erro ao buscar bursts: ".concat(response.status));
                    }
                    return [4 /*yield*/, response.json()];
                case 2:
                    body = _a.sent();
                    return [2 /*return*/, Array.isArray(body.data) ? body.data : []];
            }
        });
    });
}
export function resolveMonitoring(token_1) {
    return __awaiter(this, arguments, void 0, function (token, mode, overrides) {
        var url, response, body;
        if (mode === void 0) { mode = "PADRAO"; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    url = new URL("/monitoring/resolve", API_BASE_URL);
                    return [4 /*yield*/, fetch(url, {
                            method: "POST",
                            headers: buildHeaders(token, { "Content-Type": "application/json" }),
                            body: JSON.stringify(__assign({ modo: mode }, overrides)),
                        })];
                case 1:
                    response = _a.sent();
                    if (!response.ok) {
                        throw new Error("Erro ao resolver preset: ".concat(response.status));
                    }
                    return [4 /*yield*/, response.json()];
                case 2:
                    body = _a.sent();
                    return [2 /*return*/, body.data];
            }
        });
    });
}
export function fetchChannelConfig(token) {
    return __awaiter(this, void 0, void 0, function () {
        var response;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/config/me", API_BASE_URL), {
                        headers: buildHeaders(token),
                    })];
                case 1:
                    response = _a.sent();
                    if (!response.ok) {
                        throw new Error("Erro ao carregar configura\u00E7\u00F5es: ".concat(response.status));
                    }
                    return [2 /*return*/, response.json()];
            }
        });
    });
}
export function updateChannelConfig(token, payload) {
    return __awaiter(this, void 0, void 0, function () {
        var response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/config/me", API_BASE_URL), {
                        method: "PUT",
                        headers: buildHeaders(token, { "Content-Type": "application/json" }),
                        body: JSON.stringify(payload),
                    })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Erro ao atualizar configura\u00E7\u00E3o: ".concat(response.status));
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function attachChannelStreamer(token, payload) {
    return __awaiter(this, void 0, void 0, function () {
        var response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/config/me/streamers", API_BASE_URL), {
                        method: "POST",
                        headers: buildHeaders(token, { "Content-Type": "application/json" }),
                        body: JSON.stringify(payload),
                    })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Erro ao adicionar streamer: ".concat(response.status));
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function detachChannelStreamer(token, streamerId) {
    return __awaiter(this, void 0, void 0, function () {
        var response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/config/me/streamers/".concat(streamerId), API_BASE_URL), {
                        method: "DELETE",
                        headers: buildHeaders(token),
                    })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Erro ao remover streamer: ".concat(response.status));
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function reorderChannelStreamers(token, streamerIds) {
    return __awaiter(this, void 0, void 0, function () {
        var response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/config/me/streamers/reorder", API_BASE_URL), {
                        method: "POST",
                        headers: buildHeaders(token, { "Content-Type": "application/json" }),
                        body: JSON.stringify({ streamer_ids: streamerIds }),
                    })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Erro ao reordenar streamers: ".concat(response.status));
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function fetchDeliveryHistory(token_1) {
    return __awaiter(this, arguments, void 0, function (token, limit) {
        var url, response;
        if (limit === void 0) { limit = 50; }
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    url = new URL("/config/me/history", API_BASE_URL);
                    url.searchParams.set("limit", String(limit));
                    return [4 /*yield*/, fetch(url, {
                            headers: buildHeaders(token),
                        })];
                case 1:
                    response = _a.sent();
                    if (!response.ok) {
                        throw new Error("Erro ao carregar hist\u00F3rico: ".concat(response.status));
                    }
                    return [2 /*return*/, response.json()];
            }
        });
    });
}
export function refreshSession(refreshToken) {
    return __awaiter(this, void 0, void 0, function () {
        var response, body;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0: return [4 /*yield*/, fetch(new URL("/auth/refresh", API_BASE_URL), {
                        method: "POST",
                        headers: buildHeaders(null, { "Content-Type": "application/json" }),
                        body: JSON.stringify({ refresh_token: refreshToken }),
                    })];
                case 1:
                    response = _b.sent();
                    if (!!response.ok) return [3 /*break*/, 3];
                    return [4 /*yield*/, response.json().catch(function () { return ({}); })];
                case 2:
                    body = _b.sent();
                    throw new Error((_a = body === null || body === void 0 ? void 0 : body.detail) !== null && _a !== void 0 ? _a : "Não foi possível atualizar a sessão");
                case 3: return [2 /*return*/, response.json()];
            }
        });
    });
}
export function logoutRequest(token) {
    return __awaiter(this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!token) {
                        return [2 /*return*/];
                    }
                    return [4 /*yield*/, fetch(new URL("/auth/logout", API_BASE_URL), {
                            method: "POST",
                            headers: buildHeaders(token),
                        })];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
