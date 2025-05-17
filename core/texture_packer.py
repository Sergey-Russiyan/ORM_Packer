import os
import re
from PIL import Image


class TexturePackerCore:
    @staticmethod
    def get_suffixes(suffix_str):
        return [s.strip().lower() for s in suffix_str.split(",") if s.strip()]

    @staticmethod
    def process_texture(base, maps, output_folder, suffixes):
        try:
            # Use user-configured keys (e.g. 'ambient_occlusion', 'roughness', 'metallic')
            ao_path = maps.get(suffixes['ao'])
            rough_path = maps.get(suffixes['roughness'])
            metal_path = maps.get(suffixes['metallic'])

            if not ao_path or not rough_path or not metal_path:
                return False, "Missing one or more required texture maps"

            ao_img = Image.open(ao_path).convert("L")
            rough_img = Image.open(rough_path).convert("L")
            metal_img = Image.open(metal_path).convert("L")

            if ao_img.size != rough_img.size or ao_img.size != metal_img.size:
                return False, "Image sizes do not match"

            orm_img = Image.merge("RGB", (ao_img, rough_img, metal_img))
            out_path = os.path.join(output_folder, f"{base}_ORM.png")
            orm_img.save(out_path, optimize=True)
            return True, f"Packed {base}_ORM.png"

        except Exception as e:
            return False, str(e)

    @staticmethod
    def find_textures(folder, suffixes):
        # suffixes: {'ao': 'ambient_occlusion', 'roughness': 'roughness', 'metallic': 'metallic'}
        suffix_lists = {
            'ao': TexturePackerCore.get_suffixes(suffixes['ao']),
            'roughness': TexturePackerCore.get_suffixes(suffixes['roughness']),
            'metallic': TexturePackerCore.get_suffixes(suffixes['metallic']),
        }

        # Create a lookup to map suffix -> type (ao, roughness, metallic)
        suffix_to_type = {}
        for tex_type, suffix_list in suffix_lists.items():
            for sfx in suffix_list:
                suffix_to_type[sfx] = tex_type

        all_suffixes = list(suffix_to_type.keys())
        pattern = re.compile(
            rf"(.+?)_({'|'.join(re.escape(s) for s in all_suffixes)})\.(png|jpg)$",
            re.IGNORECASE
        )

        textures = {}
        for filename in os.listdir(folder):
            if match := pattern.match(filename):
                base = match.group(1)
                suffix = match.group(2).lower()
                tex_type = suffix_to_type[suffix]  # e.g. 'ao', 'roughness', 'metallic'

                user_key = suffixes[tex_type]  # e.g. 'ambient_occlusion'
                textures.setdefault(base, {})[user_key] = os.path.join(folder, filename)

        return textures