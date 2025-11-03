require("dotenv").config();
const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const PORT = process.env.PORT || 3001;
const GQL_ENDPOINT = "https://gql.twitch.tv/gql";
const IG_GRAPH_BASE = "https://graph.facebook.com/v20.0";

const IG_USER_ID = process.env.IG_USER_ID || "";
const IG_ACCESS_TOKEN = process.env.IG_ACCESS_TOKEN || "";
const SOCIAL_JOB_TOKEN = process.env.SOCIAL_JOB_API_TOKEN || process.env.SOCIAL_JOB_SECRET || "";
const SOCIAL_EXPORT_BASE_URL =
  process.env.SOCIAL_EXPORT_BASE_URL ||
  process.env.PUBLIC_BASE_URL ||
  "";
const JOB_TIMEOUT_PUBLISH_MINUTES = parseInt(
  process.env.SOCIAL_JOB_TIMEOUT_MINUTES || "10",
  10
);
const JOB_POLL_INTERVAL_SECONDS = parseInt(
  process.env.SOCIAL_JOB_POLL_INTERVAL_SECONDS || "8",
  10
);

const app = express();
app.use(cors());
app.use(express.json({ limit: "2mb" }));

// Utilitário simples para ler booleanos de variáveis de ambiente
const parseBool = (v) => {
  const s = String(v || "").trim().toLowerCase();
  return s === "1" || s === "true" || s === "yes" || s === "on";
};

// Healthcheck em duas rotas para compatibilidade com proxy_pass
const healthHandler = (_req, res) => {
  const exportsDir = process.env.EXPORTS_DIR || path.resolve(__dirname, "exports");
  let exportsReady = false;
  try {
    const stat = fs.statSync(exportsDir);
    exportsReady = stat.isDirectory();
  } catch (_) {}
  res.status(200).json({ status: "ok", port: PORT, exportsDir, exportsReady });
};
app.get("/api/health", healthHandler);
app.get("/health", healthHandler);

// --- Rotas para servir vídeos exportados (para Instagram/TikTok) ---
const EXPORTS_DIR = process.env.EXPORTS_DIR || path.resolve(__dirname, "exports");
const TEMP_DIR = process.env.SOCIAL_TEMP_DIR || path.resolve(__dirname, "temp");

const ensureDir = (dir) => {
  try {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`📁 Pasta pronta: ${dir}`);
  } catch (e) {
    console.error(`❌ Não foi possível preparar a pasta '${dir}':`, e.message);
  }
};

ensureDir(EXPORTS_DIR);
ensureDir(TEMP_DIR);

app.use(
  "/social/exports",
  express.static(EXPORTS_DIR, {
    acceptRanges: true,
    etag: true,
    setHeaders: (res, filePath) => {
      // Garante Content-Type adequado e cache agressivo
      if (filePath.endsWith(".mp4")) {
        res.setHeader("Content-Type", "video/mp4");
      }
      res.setHeader("Cache-Control", "public, max-age=604800, immutable");
    },
  })
);

// --- INÍCIO DA ALTERAÇÃO: CORREÇÃO DO TIPO DA VARIÁVEL ---
// Trocamos "$slug: String!" por "$slug: ID!" para corresponder ao que a API da Twitch espera.
const createClipPayload = (slug) => ({
  operationName: "VideoAccessToken_Clip",
  variables: {
    slug: slug,
  },
  query: `query VideoAccessToken_Clip($slug: ID!) { 
        clip(slug: $slug) {
            id
            playbackAccessToken(
                params: {platform: "web", playerBackend: "mediaplayer", playerType: "site"}
            ) {
                signature
                value
            }
            videoQualities {
                frameRate
                quality
                sourceURL
            }
        }
    }`,
});
// --- FIM DA ALTERAÇÃO ---

// Handler compartilhado para manter compatível com Nginx que remove prefixo /api
const clipHandler = async (req, res) => {
  const { slug } = req.params;
  if (!slug) {
    return res.status(400).json({ error: "Slug do clipe não fornecido." });
  }
  console.log(
    `🔎 Recebida requisição para o slug [${slug}] usando o método GQL...`
  );

  const payload = createClipPayload(slug);

  try {
    const response = await axios.post(GQL_ENDPOINT, payload, {
      headers: {
        "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "Content-Type": "application/json",
      },
    });

    const clipData = response.data?.data?.clip;

    if (
      !clipData ||
      !clipData.playbackAccessToken ||
      !clipData.videoQualities ||
      clipData.videoQualities.length === 0
    ) {
      const errorMessage = `Clipe com slug '${slug}' não encontrado ou não possui fontes de vídeo.`;
      console.log(
        `⚠️ ${errorMessage} Resposta da API:`,
        JSON.stringify(response.data)
      );
      return res
        .status(404)
        .json({ error: "Clipe não encontrado ou pode ter sido removido." });
    }

    const bestQuality = clipData.videoQualities[0];
    const downloadUrl = bestQuality.sourceURL;

    const finalUrl = `${downloadUrl}?sig=${
      clipData.playbackAccessToken.signature
    }&token=${encodeURIComponent(clipData.playbackAccessToken.value)}`;

    console.log(`✅ URL de download GQL construída com sucesso!`);
    res.status(200).json({ downloadUrl: finalUrl });
  } catch (error) {
    const errorMessage = error.response
      ? JSON.stringify(error.response.data)
      : error.message;
    console.error(
      `❌ Erro ao processar o slug '${slug}' via GQL:`,
      errorMessage
    );
    res.status(500).json({
      error:
        "Ocorreu um erro no servidor ao tentar buscar o clipe via GQL.",
    });
  }
};

// Expõe tanto com prefixo quanto sem, dependendo do proxy
app.get("/api/clip/:slug", clipHandler);
app.get("/clip/:slug", clipHandler);

// Força download no navegador: faz proxy do MP4 e define Content-Disposition
app.get("/api/clip/:slug/download", async (req, res) => {
  const { slug } = req.params;
  if (!slug) {
    return res.status(400).json({ error: "Slug do clipe não fornecido." });
  }
  try {
    const signedUrl = await fetchSignedDownloadUrl(slug);
    if (!signedUrl) {
      return res
        .status(404)
        .json({ error: "Clipe não encontrado ou URL inválida." });
    }

    // Modo por requisição: ?mode=proxy ou ?mode=redirect
    const qMode = String(req.query.mode || "").trim().toLowerCase();
    const envForceProxy = parseBool(process.env.FORCE_PROXY_DOWNLOAD);
    const doProxy = qMode === "proxy" || (envForceProxy && qMode !== "redirect");

    if (!doProxy) {
      // Redireciona sempre (zero uso de banda da VPS)
      return res.redirect(302, signedUrl);
    }

    // Proxy com Content-Disposition para forçar download
    const filename = `${sanitizeFilename(slug, "clip")}.mp4`;
    const upstream = await axios.get(signedUrl, { responseType: "stream" });

    if (upstream.headers["content-length"]) {
      res.setHeader("Content-Length", upstream.headers["content-length"]);
    }
    res.setHeader("Content-Type", "video/mp4");
    res.setHeader("Content-Disposition", `attachment; filename="${filename}"`);
    res.setHeader("Cache-Control", "no-store");

    upstream.data.on("error", (err) => {
      console.error("❌ Erro no stream upstream:", err?.message || err);
      if (!res.headersSent) {
        res.status(502).end("Erro ao transferir mídia");
      } else {
        res.destroy(err);
      }
    });

    upstream.data.pipe(res);
  } catch (error) {
    const status = error?.response?.status || 500;
    const message = error?.message || "Erro inesperado";
    console.error("❌ Falha ao preparar download do clipe:", status, message);
    res.status(status >= 400 && status < 600 ? status : 500).json({
      error: "Falha ao preparar download do clipe.",
      details: message,
    });
  }
});

// Rota sem prefixo /api (compatibilidade com proxy que remove prefixos)
app.get("/clip/:slug/download", async (req, res) => {
  req.url = `/api/clip/${req.params.slug}/download`;
  return app._router.handle(req, res, () => {});
});

// ---------------------------------------------------------------------------
// Publicação social – recepção assíncrona de jobs vindos do bot Telegram
// ---------------------------------------------------------------------------

const jobQueue = [];
let processing = false;

const enqueueJob = (job) => {
  jobQueue.push(job);
  processQueue();
};

const sanitizeFilename = (value, fallback = "video") => {
  if (!value || typeof value !== "string") return fallback;
  return value.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 80) || fallback;
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const buildSignedUrlFromClipData = (clipData) => {
  const token = clipData?.playbackAccessToken?.value;
  const sig = clipData?.playbackAccessToken?.signature;
  const quality = clipData?.videoQualities?.[0]?.sourceURL;
  if (!token || !sig || !quality) {
    return null;
  }
  return `${quality}?sig=${sig}&token=${encodeURIComponent(token)}`;
};

const fetchSignedDownloadUrl = async (slug) => {
  const payload = createClipPayload(slug);
  try {
    const { data } = await axios.post(GQL_ENDPOINT, payload, {
      headers: {
        "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",
        "Content-Type": "application/json",
      },
    });
    const clipData = data?.data?.clip;
    return buildSignedUrlFromClipData(clipData);
  } catch (error) {
    const message = error.response
      ? JSON.stringify(error.response.data)
      : error.message;
    console.error(
      `❌ Falha ao obter URL assinada via GQL para slug '${slug}':`,
      message
    );
    return null;
  }
};

const downloadWithFallback = async (candidates, slug, destino) => {
  const urls = Array.isArray(candidates) ? [...candidates] : [];

  for (const url of urls) {
    if (!url) continue;
    try {
      await streamToFile(url, destino);
      return url;
    } catch (error) {
      const status = error.response?.status;
      if (status === 403 || status === 404) {
        console.warn(`⚠️ URL indisponível (${status}) em ${url}. Tentando próxima...`);
        continue;
      }
      throw error;
    }
  }

  const signedUrl = await fetchSignedDownloadUrl(slug);
  if (!signedUrl) {
    throw new Error("Não foi possível obter URL válida para download do clipe.");
  }
  await streamToFile(signedUrl, destino);
  return signedUrl;
};

const streamToFile = async (url, destino) => {
  await fs.promises.mkdir(path.dirname(destino), { recursive: true });
  const response = await axios.get(url, {
    responseType: "stream",
    timeout: 60000,
  });

  return new Promise((resolve, reject) => {
    const writer = fs.createWriteStream(destino);
    response.data.pipe(writer);
    writer.on("finish", resolve);
    writer.on("error", reject);
  });
};

const runFfmpeg = (inputPath, outputPath, maxDuration) => {
  const { spawn } = require("child_process");
  return new Promise((resolve, reject) => {
    const args = [
      "-y",
      "-i",
      inputPath,
      "-t",
      String(maxDuration || 57),
      "-vf",
      "scale=-2:1920,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,setsar=1",
      "-c:v",
      "libx264",
      "-preset",
      "veryfast",
      "-crf",
      "23",
      "-c:a",
      "aac",
      "-b:a",
      "128k",
      "-movflags",
      "+faststart",
      outputPath,
    ];

    const ffmpeg = spawn("ffmpeg", args, { stdio: ["ignore", "pipe", "pipe"] });
    let stderr = "";
    ffmpeg.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    ffmpeg.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        console.error("❌ ffmpeg falhou:", stderr.slice(-500));
        reject(new Error(`ffmpeg exited with code ${code}`));
      }
    });
  });
};

const publishInstagram = async (videoUrl, caption, shareToFeed) => {
  if (!IG_USER_ID || !IG_ACCESS_TOKEN) {
    throw new Error("Instagram não configurado no ambiente.");
  }

  const paramsCreate = new URLSearchParams({
    media_type: "REELS",
    video_url: videoUrl,
    caption: caption || "",
    thumb_offset: "1",
    share_to_feed: shareToFeed ? "true" : "false",
    access_token: IG_ACCESS_TOKEN,
  });

  const creation = await axios.post(
    `${IG_GRAPH_BASE}/${IG_USER_ID}/media`,
    paramsCreate
  );

  const creationId = creation.data?.id;
  if (!creationId) {
    throw new Error("Resposta inesperada ao criar container do Reel.");
  }

  const maxWaitMs = (JOB_TIMEOUT_PUBLISH_MINUTES || 10) * 60 * 1000;
  const pollIntervalMs = (JOB_POLL_INTERVAL_SECONDS || 8) * 1000;
  let elapsed = 0;

  while (elapsed <= maxWaitMs) {
    const statusResp = await axios.get(
      `${IG_GRAPH_BASE}/${creationId}?fields=status_code&access_token=${IG_ACCESS_TOKEN}`
    );
    const statusCode = statusResp.data?.status_code;
    if (statusCode === "FINISHED") {
      break;
    }
    if (statusCode === "ERROR") {
      throw new Error("Instagram retornou status ERROR durante processamento do Reel.");
    }
    await sleep(pollIntervalMs);
    elapsed += pollIntervalMs;
  }

  if (elapsed > maxWaitMs) {
    throw new Error("Tempo excedido aguardando processamento do Reel no Instagram.");
  }

  const publishParams = new URLSearchParams({
    creation_id: creationId,
    access_token: IG_ACCESS_TOKEN,
  });

  const publish = await axios.post(
    `${IG_GRAPH_BASE}/${IG_USER_ID}/media_publish`,
    publishParams
  );

  return publish.data?.id || null;
};

const processJob = async (job) => {
  const clipId = job.clip_id || job.slug || Date.now().toString();
  const fileSafeId = sanitizeFilename(clipId, `clip-${Date.now()}`);
  const rawPath = path.join(TEMP_DIR, `${fileSafeId}_src.mp4`);
  const exportPath = path.join(EXPORTS_DIR, `${fileSafeId}.mp4`);

  console.log(`📥 Processando job social para clip ${clipId}...`);
  try {
    await downloadWithFallback(job.mp4_candidates, job.slug, rawPath);
    await runFfmpeg(rawPath, exportPath, job.max_duration_seconds);
  } catch (error) {
    console.error(
      "❌ Falha durante download ou edição do clip",
      clipId,
      error
    );
    throw error;
  }

  try {
    await fs.promises.unlink(rawPath);
  } catch (err) {
    if (err.code !== "ENOENT") {
      console.warn("⚠️ Não foi possível remover arquivo temporário", rawPath, err.message);
    }
  }

  const publicBase = SOCIAL_EXPORT_BASE_URL || "";
  const publicUrl = publicBase
    ? `${publicBase.replace(/\/$/, "")}/${path.basename(exportPath)}`
    : `${job.public_base_url || ""}${path.basename(exportPath)}`;

  if (job.platforms?.includes("instagram")) {
    const mediaId = await publishInstagram(
      publicUrl,
      job.caption,
      job.instagram_share_to_feed
    );
    console.log(`✅ Reel publicado com sucesso (media_id=${mediaId || "?"}).`);
  } else {
    console.log("ℹ️ Plataforma Instagram não inclusa; pulando publicação.");
  }

  if (job.platforms?.includes("tiktok")) {
    console.log(
      "ℹ️ TikTok ainda não implementado. Arquivo pronto para upload manual:",
      exportPath
    );
  }

  console.log(`🏁 Job concluído para clip ${clipId}. Arquivo: ${exportPath}`);
};

const processQueue = async () => {
  if (processing) return;
  processing = true;
  while (jobQueue.length) {
    const job = jobQueue.shift();
    try {
      await processJob(job);
    } catch (error) {
      console.error(`❌ Falha ao processar job ${job.clip_id || job.slug}:`, error);
    }
  }
  processing = false;
};

const validateJobPayload = (body) => {
  if (!body || typeof body !== "object") {
    return "Payload inválido";
  }
  if (!body.clip_id && !body.slug) {
    return "'clip_id' ou 'slug' são obrigatórios";
  }
  if (!Array.isArray(body.platforms) || body.platforms.length === 0) {
    return "'platforms' precisa ser uma lista com pelo menos um item";
  }
  if (!body.caption) {
    return "Legenda ('caption') não foi fornecida";
  }
  return null;
};

const socialJobHandler = (req, res) => {
  if (SOCIAL_JOB_TOKEN) {
    const header = req.headers["authorization"] || "";
    const token = header.startsWith("Bearer ") ? header.slice(7) : header;
    if (token !== SOCIAL_JOB_TOKEN) {
      return res.status(401).json({ error: "Não autorizado" });
    }
  }

  const validationError = validateJobPayload(req.body);
  if (validationError) {
    return res.status(400).json({ error: validationError });
  }

  enqueueJob(req.body);
  res.status(202).json({ status: "queued", clip_id: req.body.clip_id || req.body.slug });
};

app.post("/api/social/publish", socialJobHandler);
app.post("/social/publish", socialJobHandler);

app.listen(PORT, () => {
  console.log(`🚀 API do Clipador (GQL) rodando em http://localhost:${PORT}`);
});
