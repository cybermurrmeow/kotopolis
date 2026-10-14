from PIL import Image

from media import PREVIEW_SIZE, create_catalog_previews, media_paths


def test_animated_gif_keeps_animation_in_catalog_preview(tmp_path):
    source = tmp_path / "cat.gif"
    first = Image.new("RGB", (320, 480), "#f5a3c7")
    second = Image.new("RGB", (320, 480), "#7d6bd1")
    first.save(
        source,
        save_all=True,
        append_images=[second],
        duration=[80, 120],
        loop=0,
    )

    poster, animated = create_catalog_previews(source, tmp_path / "catalog_previews")

    with Image.open(poster) as image:
        assert image.size == PREVIEW_SIZE
        assert getattr(image, "n_frames", 1) == 1

    with Image.open(animated) as image:
        assert image.size == PREVIEW_SIZE
        assert image.n_frames == 2


def test_media_paths_uses_previews_and_safe_placeholder(tmp_path):
    static_folder = tmp_path / "static"
    source = static_folder / "uploads" / "cat_media" / "cat.png"
    source.parent.mkdir(parents=True)
    Image.new("RGB", (100, 100), "white").save(source)
    create_catalog_previews(source, source.parent / "catalog_previews")

    paths = media_paths("uploads/cat_media/cat.png", static_folder)
    assert paths["poster"].endswith("cat-poster.webp")
    assert paths["animated"].endswith("cat-anim.webp")
    assert media_paths(None, static_folder)["poster"] == "img/cat-placeholder.svg"
