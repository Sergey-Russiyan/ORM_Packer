# 🧃 Texture Packer — ORM Map Generator

**Texture Packer** is a simple tool designed for 3D artists and game modders. It helps you **combine three texture maps** (Ambient Occlusion, Roughness, and Metallic) into a single **ORM texture** used in game engines like Unreal Engine and Unity.

No coding skills required. Just drag your textures into a folder and run the packer!

---

## 🧩 What is an ORM Texture?

An ORM (Occlusion-Roughness-Metallic) texture combines:

- **Red channel**: Ambient Occlusion (AO)
- **Green channel**: Roughness
- **Blue channel**: Metallic

Game engines use these combined textures to save memory and optimize performance.

---

## 🎨 How to Use

### 1. 💾 Prepare Your Textures

Put all your textures in one folder. Name them using a clear suffix like:

MyModel_ao.png
MyModel_roughness.png
MyModel_metallic.png


You can also use alternative endings like:

MyModel_ambient_occlusion.png
MyModel_rough.png


The tool lets you configure these suffixes.

---

### 2. ⚙️ Choose Your Settings

When you launch the app:

1. **Select the folder** with your textures.
2. **Set suffixes** for AO, Roughness, and Metallic maps. Example:
   - AO: `ao,ambient_occlusion`
   - Roughness: `rough,roughness`
   - Metallic: `metal,metallic`
3. (Optional) Enable **Log to File** to save the output report.

---

### 3. 🚀 Start Packing

Click the **Start** button and let the tool do its magic.

It will check if all required maps are available for each model and create a new `*_ORM.png` file in the same folder.

Example output:

MyModel_ORM.png


---

## ✅ Features

- Supports **.png** and **.jpg** formats
- Accepts **multiple suffix names** per map
- Checks for **missing or mismatched textures**
- Creates a compact **ORM texture**
- Optional logging to a text file

---

## 📁 Output Location

The packed files will be saved **in the same folder** as your source textures.

If you enable logging, a file like this will be created:

packing_log_20250515.txt


---

## 🛠 Troubleshooting

- **Missing maps?**  
  Make sure your textures use the correct suffixes (e.g., `ao`, `roughness`, `metallic`).

- **Different image sizes?**  
  All three maps must be the same size. Resize them in Photoshop or any image editor.

- **Nothing happens?**  
  Check the log file (if enabled) for skipped files or errors.

---

## 🙋 FAQ

### Can I use other suffixes like `_occlusion` or `_met`?
Yes! Just type your preferred endings in the suffix settings, separated by commas.

Example:

AO: ao,ambient_occlusion,occlusion
Metallic: metallic,metal,met


---

### Does it overwrite original textures?
No, the tool only creates new `*_ORM.png` files. Your original textures are safe.

---

## ❤️ Made for Artists

This tool was made to **save your time** and **remove the technical hassle**. Focus on your art — let the packer handle the boring bits.

---

## 📩 Feedback or Ideas?

Have a feature request or bug to report? Let us know!







