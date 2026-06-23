from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Seera Chatbot API"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./seera_chatbot.db"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # ---- Image-based skin analysis (FR-IMG-02/04, NFR-IMG-03) ----
    IMAGE_MAX_UPLOAD_BYTES: int = 5 * 1024 * 1024
    IMAGE_MIN_DIMENSION: int = 200
    IMAGE_BRIGHTNESS_MIN: float = 50.0
    IMAGE_BRIGHTNESS_MAX: float = 215.0
    IMAGE_BLUR_THRESHOLD: float = 45.0
    IMAGE_MIN_FACE_RATIO: float = 0.15
    IMAGE_MIN_SKIN_PIXELS: int = 150
    IMAGE_CONFIDENCE_THRESHOLD: float = 0.6

    # ---- Realistic Virtual Try-On (PRD Revisi IDM-VTON yisol AssetTier, NFR-VTO) ----
    # Mode inference: "space" (HuggingFace Space via gradio_client),
    # "http" (worker GPU internal), "mock" (uji/demo tanpa GPU), "disabled".
    # PRD Revisi: IDM-VTON (provider resmi yisol) = model default (garment fidelity);
    # CatVTON = fallback/demo/pembanding.
    VTON_MODEL_DEFAULT: str = "idm-vton"
    VTON_MODEL_VERSION: str = "idm-vton-prototype"
    # Metadata provider resmi (PRD 15.2) — dicatat per job untuk ketelusuran.
    VTON_MODEL_PROVIDER: str = "yisol"
    VTON_MODEL_NAME: str = "IDM-VTON"
    VTON_MODEL_REPO: str = "yisol/IDM-VTON"
    VTON_FALLBACK_MODEL: str = "catvton"
    VTON_GARMENT_FIDELITY_PRIORITY: bool = True
    VTON_INFERENCE_MODE: str = "space"
    # VTON_SPACE_ID adalah Space default (IDM-VTON); alias historis VTON_IDM_SPACE_ID
    # tetap didukung agar konfigurasi lama tidak rusak.
    VTON_SPACE_ID: str = "yisol/IDM-VTON"
    VTON_IDM_SPACE_ID: str = "yisol/IDM-VTON"
    VTON_CATVTON_SPACE_ID: str = "zhengchong/CatVTON"
    VTON_HTTP_URL: str = ""
    VTON_HF_TOKEN: str = ""
    VTON_INFERENCE_RESOLUTION: str = "768x1024"
    # ---- VTON Asset Eligibility Tier & experimental mode (FR-VTO-15/16/17) ----
    # Produk dengan foto "seadanya" boleh diproses dalam mode experimental/limited.
    VTON_ALLOW_EXPERIMENTAL_ASSET_MODE: bool = True
    # Aset vton_not_supported tidak pernah dikirim ke model.
    VTON_BLOCK_UNSUPPORTED_ASSETS: bool = True
    # Simpan artefak debug (input/mask/output/metadata) per job untuk evaluasi.
    VTON_ENABLE_DEBUG_ARTIFACTS: bool = True
    VTON_DEBUG_DIR: str = "storage/vton_debug"
    # IDM-VTON (default) — denoise steps + auto crop person-agnostic
    VTON_IDM_DENOISE_STEPS: int = 30
    VTON_IDM_AUTO_CROP: bool = False
    # CatVTON (fallback) — parameter diffusion
    VTON_NUM_INFERENCE_STEPS: int = 50
    VTON_GUIDANCE_SCALE: float = 2.5
    VTON_SEED: int = 42
    VTON_TIMEOUT_SECONDS: int = 300
    VTON_MAX_JOBS_PER_SESSION: int = 5
    VTON_TEMP_DIR: str = "/tmp/seera_vton"
    VTON_IMAGE_TTL_MINUTES: int = 60
    # Foto upper-body: wajah tidak boleh mendominasi frame (BR-VTO-01)
    VTON_MAX_FACE_HEIGHT_RATIO: float = 0.40
    VTON_MIN_BELOW_FACE_RATIO: float = 1.1
    # Eksekusi job sinkron (dipakai test agar deterministik)
    VTON_SYNC_MODE: bool = False
    # Lisensi IDM-VTON/CatVTON non-komersial: prototipe akademik saja (BR-VTO-18)
    VTON_COMMERCIAL_DEPLOYMENT_ALLOWED: bool = False

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
