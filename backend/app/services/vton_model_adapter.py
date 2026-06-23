"""VTONModelAdapter: abstraksi model realistic virtual try-on (NFR-VTO-06).

PRD Revisi IDM-VTON: **IDM-VTON adalah model default prototipe** (BR-VTO-13)
karena kebutuhan utama fitur adalah garment fidelity — kesesuaian detail
pakaian (motif, kerah, lengan, kancing, warna) terhadap produk asli.
**CatVTON diposisikan sebagai fallback/demo ringan/model pembanding**
(BR-VTO-14). Penggantian model murni lewat konfigurasi — FIS/ROC tidak tersentuh.

Catatan lisensi (BR-VTO-18): IDM-VTON & CatVTON berlisensi non-komersial;
penggunaan di sini terbatas untuk riset/prototipe akademik.
"""
import inspect
import io
import tempfile
from abc import ABC, abstractmethod
from typing import Optional

from PIL import Image

from app.core.config import settings


class VTONInferenceError(Exception):
    """Kegagalan inference yang harus membuat job FAILED tanpa mengganggu chatbot."""


def _make_space_client(space_id: str):
    """Bangun gradio_client.Client lintas versi (hf_token <=1.x vs token >=2.x)."""
    try:
        from gradio_client import Client
    except ImportError as exc:
        raise VTONInferenceError("gradio_client tidak terpasang pada server.") from exc

    params = inspect.signature(Client.__init__).parameters
    kwargs = {}
    token = settings.VTON_HF_TOKEN or None
    if token:
        if "hf_token" in params:
            kwargs["hf_token"] = token
        elif "token" in params:
            kwargs["token"] = token
    if "verbose" in params:
        kwargs["verbose"] = False
    # Inference difusi bisa lama; perpanjang read timeout httpx internal
    # gradio_client agar koneksi tidak putus saat Space memproses (NFR-VTO-01).
    if "httpx_kwargs" in params:
        kwargs["httpx_kwargs"] = {"timeout": float(settings.VTON_TIMEOUT_SECONDS)}
    return Client(space_id, **kwargs)


def _wrap_space_error(model_label: str, exc: Exception) -> VTONInferenceError:
    detail = str(exc)
    if "quota" in detail.lower():
        return VTONInferenceError(
            f"Kuota GPU layanan {model_label} sedang habis. Coba lagi nanti, atau "
            "konfigurasikan token HuggingFace (VTON_HF_TOKEN) untuk kuota lebih besar."
        )
    return VTONInferenceError(f"Inference {model_label} Space gagal: {detail}")


def _result_image_bytes(result_path: str, model_label: str) -> bytes:
    if not result_path:
        raise VTONInferenceError(f"{model_label} tidak mengembalikan output image.")
    with Image.open(result_path) as img:
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()


def _blank_layer_for(person_path: str) -> str:
    """Layer ImageEditor kosong (transparan, seukuran foto person).

    App gradio kedua model mengakses person_image["layers"] dari komponen
    ImageEditor; layer kosong yang seragam membuat app beralih ke automasker
    internal (kualitas mask terbaik).
    """
    with Image.open(person_path) as person:
        blank = Image.new("RGBA", person.size, (0, 0, 0, 0))
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    blank.save(tmp, format="PNG")
    tmp.close()
    return tmp.name


def _garment_on_white(garment_path: str) -> str:
    """Flatten garment cutout (alpha) ke latar putih bersih.

    Garment encoder model VTON mengasumsikan background bersih/terang
    (FR-VTO-08); alpha transparan akan menjadi hitam bila tidak diflatten.
    """
    with Image.open(garment_path) as garment:
        if garment.mode != "RGBA":
            return garment_path
        white = Image.new("RGB", garment.size, (255, 255, 255))
        white.paste(garment, (0, 0), garment)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    white.save(tmp, format="PNG")
    tmp.close()
    return tmp.name


class VTONModelAdapter(ABC):
    name: str = "unknown"

    @property
    def version(self) -> str:
        return settings.VTON_MODEL_VERSION

    @abstractmethod
    def infer(
        self,
        person_path: str,
        garment_path: str,
        cloth_type: str,
        mask_path: Optional[str] = None,
        garment_caption: Optional[str] = None,
    ) -> bytes:
        """Jalankan try-on; kembalikan bytes PNG hasil. Raise VTONInferenceError bila gagal."""

    def inference_parameters(self) -> dict:
        """Parameter inference untuk ketelusuran pada vton_jobs (BR-VTO-13)."""
        return {
            "mode": settings.VTON_INFERENCE_MODE,
            "resolution": settings.VTON_INFERENCE_RESOLUTION,
            "seed": settings.VTON_SEED,
        }


class IDMVTONAdapter(VTONModelAdapter):
    """Model default prototipe (BR-VTO-13): garment fidelity diprioritaskan.

    Mode "space" memanggil HuggingFace Space resmi yisol/IDM-VTON endpoint
    /tryon (terverifikasi live): person ImageEditor dict, garment image,
    garment_des (caption), is_checked (automask), is_checked_crop,
    denoise_steps, seed → [output, masked].
    """

    name = "IDM-VTON"

    @property
    def version(self) -> str:
        return settings.VTON_MODEL_VERSION

    @staticmethod
    def _space_id() -> str:
        # PRD 15.2: VTON_SPACE_ID resmi = yisol/IDM-VTON; alias lama tetap didukung.
        return settings.VTON_SPACE_ID or settings.VTON_IDM_SPACE_ID

    def inference_parameters(self) -> dict:
        return {
            **super().inference_parameters(),
            "model_provider": settings.VTON_MODEL_PROVIDER,
            "model_name": settings.VTON_MODEL_NAME,
            "model_repo": settings.VTON_MODEL_REPO,
            "space_id": self._space_id(),
            "denoise_steps": settings.VTON_IDM_DENOISE_STEPS,
            "auto_mask": True,
            "auto_crop": settings.VTON_IDM_AUTO_CROP,
        }

    def infer(self, person_path, garment_path, cloth_type, mask_path=None, garment_caption=None) -> bytes:
        mode = settings.VTON_INFERENCE_MODE
        if mode == "space":
            return self._infer_space(person_path, garment_path, garment_caption)
        if mode == "http":
            return _http_infer(
                self.name, person_path, garment_path, cloth_type, mask_path, garment_caption
            )
        raise VTONInferenceError(
            f"Layanan inference IDM-VTON belum dikonfigurasi (VTON_INFERENCE_MODE={mode})."
        )

    def _infer_space(self, person_path: str, garment_path: str, garment_caption: Optional[str]) -> bytes:
        from gradio_client import handle_file

        try:
            client = _make_space_client(self._space_id())
            result = client.predict(
                dict={
                    "background": handle_file(person_path),
                    "layers": [handle_file(_blank_layer_for(person_path))],
                    "composite": None,
                },
                garm_img=handle_file(_garment_on_white(garment_path)),
                garment_des=garment_caption or "clothing item, front view",
                is_checked=True,  # automask + auto person-agnostic (preprocessing internal)
                is_checked_crop=settings.VTON_IDM_AUTO_CROP,
                denoise_steps=settings.VTON_IDM_DENOISE_STEPS,
                seed=settings.VTON_SEED,
                api_name="/tryon",
            )
        except Exception as exc:  # noqa: BLE001 - semua error space → job FAILED
            raise _wrap_space_error("IDM-VTON", exc) from exc

        # /tryon mengembalikan [output, masked_image]
        output = result[0] if isinstance(result, (list, tuple)) else result
        output_path = output if isinstance(output, str) else getattr(output, "path", None)
        return _result_image_bytes(output_path, "IDM-VTON")


class CatVTONAdapter(VTONModelAdapter):
    """Fallback/demo ringan/model pembanding (BR-VTO-14) — bukan model utama
    untuk kebutuhan garment fidelity tinggi."""

    name = "CatVTON"

    @property
    def version(self) -> str:
        return "catvton-fallback"

    def inference_parameters(self) -> dict:
        return {
            **super().inference_parameters(),
            "space_id": settings.VTON_CATVTON_SPACE_ID,
            "num_inference_steps": settings.VTON_NUM_INFERENCE_STEPS,
            "guidance_scale": settings.VTON_GUIDANCE_SCALE,
        }

    def infer(self, person_path, garment_path, cloth_type, mask_path=None, garment_caption=None) -> bytes:
        mode = settings.VTON_INFERENCE_MODE
        if mode == "space":
            return self._infer_space(person_path, garment_path, cloth_type)
        if mode == "http":
            return _http_infer(
                self.name, person_path, garment_path, cloth_type, mask_path, garment_caption
            )
        raise VTONInferenceError(
            f"Layanan inference CatVTON belum dikonfigurasi (VTON_INFERENCE_MODE={mode})."
        )

    def _infer_space(self, person_path: str, garment_path: str, cloth_type: str) -> bytes:
        from gradio_client import handle_file

        try:
            client = _make_space_client(settings.VTON_CATVTON_SPACE_ID)
            result = client.predict(
                person_image={
                    "background": handle_file(person_path),
                    "layers": [handle_file(_blank_layer_for(person_path))],
                    "composite": None,
                },
                cloth_image=handle_file(_garment_on_white(garment_path)),
                cloth_type=cloth_type,
                num_inference_steps=settings.VTON_NUM_INFERENCE_STEPS,
                guidance_scale=settings.VTON_GUIDANCE_SCALE,
                seed=settings.VTON_SEED,
                show_type="result only",
                api_name="/submit_function",
            )
        except Exception as exc:  # noqa: BLE001
            raise _wrap_space_error("CatVTON", exc) from exc

        output_path = result if isinstance(result, str) else getattr(result, "path", None)
        return _result_image_bytes(output_path, "CatVTON")


def _http_infer(model_name, person_path, garment_path, cloth_type, mask_path, garment_caption) -> bytes:
    """Worker GPU internal generik (POST multipart, balasan bytes image)."""
    if not settings.VTON_HTTP_URL:
        raise VTONInferenceError("VTON_HTTP_URL belum dikonfigurasi.")
    try:
        import httpx

        files = {
            "person_image": open(person_path, "rb"),
            "garment_image": open(garment_path, "rb"),
        }
        if mask_path:
            files["mask_image"] = open(mask_path, "rb")
        response = httpx.post(
            settings.VTON_HTTP_URL,
            files=files,
            data={
                "model": model_name,
                "cloth_type": cloth_type,
                "garment_caption": garment_caption or "",
            },
            timeout=settings.VTON_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.content
    except Exception as exc:  # noqa: BLE001
        raise VTONInferenceError(f"Worker VTON internal gagal: {exc}") from exc


class MockVTONAdapter(VTONModelAdapter):
    """Adapter mock untuk pengujian/demo tanpa GPU: komposit sederhana
    garment (alpha) pada area mask person image. Bukan hasil model generatif —
    dipakai hanya saat VTON_INFERENCE_MODE="mock"."""

    name = "MockVTON"

    @property
    def version(self) -> str:
        return "mock-compositor"

    def infer(self, person_path, garment_path, cloth_type, mask_path=None, garment_caption=None) -> bytes:
        try:
            person = Image.open(person_path).convert("RGB")
            garment = Image.open(garment_path).convert("RGBA")

            if mask_path:
                mask = Image.open(mask_path).convert("L")
                bbox = mask.getbbox() or (0, person.height // 3, person.width, person.height)
            else:
                bbox = (0, person.height // 3, person.width, person.height)

            bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            scale = min(bw / garment.width, bh / garment.height)
            gw, gh = max(1, int(garment.width * scale)), max(1, int(garment.height * scale))
            garment = garment.resize((gw, gh))
            px = bbox[0] + (bw - gw) // 2
            py = bbox[1]
            person.paste(garment, (px, py), garment)

            buf = io.BytesIO()
            person.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as exc:  # noqa: BLE001
            raise VTONInferenceError(f"Mock compositor gagal: {exc}") from exc


_ADAPTERS = {
    "idm-vton": IDMVTONAdapter,
    "catvton": CatVTONAdapter,
    "mock": MockVTONAdapter,
}


def get_adapter() -> VTONModelAdapter:
    """Adapter default dari konfigurasi; mode "mock" memaksa MockVTONAdapter."""
    if settings.VTON_INFERENCE_MODE == "mock":
        return MockVTONAdapter()
    adapter_cls = _ADAPTERS.get(settings.VTON_MODEL_DEFAULT.lower(), IDMVTONAdapter)
    return adapter_cls()


def get_fallback_adapter() -> Optional[VTONModelAdapter]:
    """Adapter fallback (BR-VTO-14): CatVTON saat resource IDM-VTON tidak tersedia.

    Hanya aktif pada mode inference nyata (space/http); None bila tidak
    dikonfigurasi atau sama dengan model default.
    """
    if settings.VTON_INFERENCE_MODE not in ("space", "http"):
        return None
    name = (settings.VTON_FALLBACK_MODEL or "").lower()
    if not name or name == settings.VTON_MODEL_DEFAULT.lower():
        return None
    adapter_cls = _ADAPTERS.get(name)
    return adapter_cls() if adapter_cls else None
