from pathlib import Path
from urllib.parse import urlparse
import os
import uuid
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_WIDTH = 10_000
MAX_HEIGHT = 10_000
MAX_PIXELS = 12_000_000
MAX_FRAMES = 300
PREVIEW_SIZE = (960, 720)
MAX_DECODED_PIXELS = 24_000_000
MAX_PREVIEW_PIXELS = 20_000_000


def _validate_budget(image):
    width, height = image.size
    frames = int(getattr(image, "n_frames", 1) or 1)
    if (
        width <= 0
        or height <= 0
        or width > MAX_WIDTH
        or height > MAX_HEIGHT
        or width * height > MAX_PIXELS
    ):
        raise ValueError("Слишком большое разрешение изображения")
    if (
        frames > MAX_FRAMES
        or width * height * frames > MAX_DECODED_PIXELS
        or PREVIEW_SIZE[0] * PREVIEW_SIZE[1] * frames > MAX_PREVIEW_PIXELS
    ):
        raise ValueError(
            "Анимация слишком велика для обработки. Уменьшите размер или число кадров"
        )
    return frames


def _validate_uploaded_image(upload):
    filename = secure_filename(upload.filename or "")
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Недопустимый формат изображения")

    stream = upload.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)

    if size <= 0:
        raise ValueError("Файл изображения пустой")
    if size > MAX_FILE_SIZE:
        raise ValueError("Размер изображения не должен превышать 10 МБ")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(stream) as image:
                _validate_budget(image)
                expected = {
                    ".jpg": "JPEG",
                    ".jpeg": "JPEG",
                    ".png": "PNG",
                    ".webp": "WEBP",
                    ".gif": "GIF",
                }
                if image.format != expected[extension]:
                    raise ValueError(
                        "Формат изображения не соответствует расширению файла"
                    )
                image.verify()
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("Слишком большое разрешение изображения") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Файл повреждён или не является изображением") from exc
    finally:
        stream.seek(0)

    return extension


def _prepare_frame(frame):
    frame = ImageOps.exif_transpose(frame)
    frame.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
    frame = frame.convert("RGBA")
    background = Image.new("RGBA", frame.size, (246, 242, 244, 255))
    background.alpha_composite(frame)
    return ImageOps.fit(
        background.convert("RGB"),
        PREVIEW_SIZE,
        method=Image.Resampling.LANCZOS,
    )


def create_catalog_previews(source_path, preview_dir):
    source_path = Path(source_path)
    preview_dir = Path(preview_dir)
    preview_dir.mkdir(parents=True, exist_ok=True)

    poster_path = preview_dir / f"{source_path.stem}-poster.webp"
    animated_path = preview_dir / f"{source_path.stem}-anim.webp"

    with Image.open(source_path) as image:
        frame_count = _validate_budget(image)
        frames = []
        durations = []

        for index in range(frame_count):
            image.seek(index)
            frames.append(_prepare_frame(image))
            durations.append(max(int(image.info.get("duration", 100) or 100), 20))

        frames[0].save(poster_path, "WEBP", quality=84, method=6)

        if len(frames) == 1:
            frames[0].save(animated_path, "WEBP", quality=84, method=6)
        else:
            frames[0].save(
                animated_path,
                "WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=int(image.info.get("loop", 0) or 0),
                quality=82,
                method=4,
            )

    return poster_path, animated_path


def save_cat_media(form, upload_folder):
    upload = form.photo.data
    if upload and getattr(upload, "filename", None):
        extension = _validate_uploaded_image(upload)
        upload_folder = Path(upload_folder)
        upload_folder.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}{extension}"
        target = upload_folder / filename

        try:
            upload.save(target)
            create_catalog_previews(target, upload_folder / "catalog_previews")
        except Exception as error:
            target.unlink(missing_ok=True)
            (upload_folder / "catalog_previews" / f"{target.stem}-poster.webp").unlink(
                missing_ok=True
            )
            (upload_folder / "catalog_previews" / f"{target.stem}-anim.webp").unlink(
                missing_ok=True
            )
            if isinstance(error, OSError):
                raise ValueError("Не удалось обработать изображение") from error
            raise

        return f"uploads/cat_media/{filename}"

    url = (form.gif_url.data or "").strip()
    if not url:
        return None

    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Укажите HTTPS-ссылку на изображение без логина и пароля")

    return url


def media_paths(photo_path, static_folder):
    if not photo_path:
        return {
            "poster": "img/cat-placeholder.svg",
            "animated": "img/cat-placeholder.svg",
            "original": "img/cat-placeholder.svg",
            "external": False,
        }

    if photo_path.startswith(("http://", "https://")):
        return {
            "poster": photo_path,
            "animated": photo_path,
            "original": photo_path,
            "external": True,
        }

    relative = Path(photo_path)
    static_root = Path(static_folder).resolve()
    original = (static_root / relative).resolve()
    if not original.is_relative_to(static_root) or not original.is_file():
        return media_paths(None, static_folder)
    preview_dir = original.parent / "catalog_previews"
    poster = preview_dir / f"{original.stem}-poster.webp"
    animated = preview_dir / f"{original.stem}-anim.webp"

    return {
        "poster": (
            str(poster.relative_to(static_folder)).replace("\\", "/")
            if poster.is_file()
            else photo_path
        ),
        "animated": (
            str(animated.relative_to(static_folder)).replace("\\", "/")
            if animated.is_file()
            else photo_path
        ),
        "original": photo_path,
        "external": False,
    }


def remove_managed_media(photo_path, upload_folder):
    if not photo_path:
        return

    relative = Path(photo_path)
    if relative.parent.as_posix() != "uploads/cat_media":
        return

    filename = relative.name
    source = (Path(upload_folder) / filename).resolve()
    if source.parent != Path(upload_folder).resolve():
        return
    preview_dir = Path(upload_folder) / "catalog_previews"

    source.unlink(missing_ok=True)
    (preview_dir / f"{source.stem}-poster.webp").unlink(missing_ok=True)
    (preview_dir / f"{source.stem}-anim.webp").unlink(missing_ok=True)
