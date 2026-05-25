import os
import re
import time
from PIL import Image


class TexturePackerCore:

    @staticmethod
    def get_suffixes(suffix_str: str) -> list[str]:
        """
        Parse a comma-separated suffix string into a clean list.
        Each suffix is stripped of whitespace and returned WITHOUT forcing
        any case change — case-normalisation happens only at match time.
        The leading underscore is part of the suffix (e.g. '_AO') and must
        NOT be stripped here, because the regex already supplies the separator.

        Before (broken): lowercased here AND an extra '_' injected by regex
            → pattern looked for base__ao.png (double underscore), never matched.
        """
        return [s.strip() for s in suffix_str.split(",") if s.strip()]

    @staticmethod
    def process_texture(
        base: str,
        maps: dict[str, str],
        output_folder: str,
        suffixes: dict[str, str],
    ) -> tuple[bool, str]:
        try:
            start_time = time.time()

            # maps keys are normalised to lowercase so lookups must be too
            ao_key    = suffixes['ao'].lower()
            rough_key = suffixes['roughness'].lower()
            metal_key = suffixes['metallic'].lower()

            ao_path    = maps.get(ao_key)
            rough_path = maps.get(rough_key)
            metal_path = maps.get(metal_key)

            if not ao_path or not rough_path or not metal_path:
                missing = [
                    k for k, v in {
                        ao_key: ao_path,
                        rough_key: rough_path,
                        metal_key: metal_path,
                    }.items()
                    if not v
                ]
                return False, f"Missing texture map(s): {', '.join(missing)}"

            ao_img    = Image.open(ao_path).convert("L")
            rough_img = Image.open(rough_path).convert("L")
            metal_img = Image.open(metal_path).convert("L")

            if ao_img.size != rough_img.size or ao_img.size != metal_img.size:
                sizes = f"AO={ao_img.size} R={rough_img.size} M={metal_img.size}"
                return False, f"Image sizes do not match: {sizes}"

            orm_img  = Image.merge("RGB", (ao_img, rough_img, metal_img))
            out_path = os.path.join(output_folder, f"{base}_ORM.png")
            orm_img.save(out_path, optimize=True)

            elapsed = time.time() - start_time
            return True, f"Packed <b>{base}_ORM</b> in <b>{elapsed:.1f}s</b>"

        except Exception as e:
            return False, str(e)

    @staticmethod
    def find_textures(folder: str, suffixes: dict[str, str]) -> dict[str, dict[str, str]]:
        """
        Scan *folder* for texture files and group them by base name.

        suffixes dict example:
            {'ao': '_AO', 'roughness': '_R', 'metallic': '_M'}

        Returned dict example:
            {
                'rock_wall': {
                    '_ao':    '/path/rock_wall_AO.png',
                    '_r':     '/path/rock_wall_R.png',
                    '_m':     '/path/rock_wall_M.png',
                }
            }

        Keys in the inner dict are always lowercase so process_texture
        can look them up with a simple .lower() normalisation.

        Fix applied:
            get_suffixes no longer lowercases, so '_AO' stays '_AO'.
            The regex matches the suffix portion WITHOUT an extra underscore
            by using a look-ahead on the base group boundary, then the suffix
            (which already contains its own leading '_') is matched directly.

            Pattern shape:  ^(.+?)(_ao|_r|_m)\.(png|jpg)$   (re.IGNORECASE)
            Correct match:  rock_wall_AO.png  →  base='rock_wall', sfx='_AO'
            Was matching:   rock_wall__ao.png (never found → 0 groups)
        """
        # Build suffix → tex_type lookup; normalise to lowercase for matching
        suffix_to_type: dict[str, str] = {}
        for tex_type, suffix_str in suffixes.items():
            for sfx in TexturePackerCore.get_suffixes(suffix_str):
                suffix_to_type[sfx.lower()] = tex_type

        if not suffix_to_type:
            return {}

        # Each suffix already contains its own leading '_', e.g. '_ao'
        # so the pattern is:  ^(base)(_ao|_r|_m)\.(png|jpg)$
        alt = '|'.join(re.escape(s) for s in suffix_to_type)
        pattern = re.compile(rf"^(.+?)({alt})\.(png|jpg)$", re.IGNORECASE)

        textures: dict[str, dict[str, str]] = {}

        for filename in os.listdir(folder):
            m = pattern.match(filename)
            if not m:
                continue

            base       = m.group(1)                    # e.g. 'rock_wall'
            sfx_raw    = m.group(2)                    # e.g. '_AO'  (original case)
            sfx_key    = sfx_raw.lower()               # e.g. '_ao'  (lookup key)
            tex_type   = suffix_to_type[sfx_key]       # e.g. 'ao'

            # Store under the *lowercased* user suffix so process_texture
            # can retrieve it with a simple .lower() call
            user_key   = suffixes[tex_type].lower()    # e.g. '_ao'
            full_path  = os.path.join(folder, filename)

            textures.setdefault(base, {})[user_key] = full_path

        return textures
