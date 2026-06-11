
### 🧃 **Texture Packer — ORM Map Generator**  
**A tool for 3D artists and game modders to combine AO, Roughness, and Metallic maps into a single ORM texture for game engines like Unreal Engine and Unity.**

---

### 🧩 **What is an ORM Texture?**  
An ORM (Occlusion-Roughness-Metallic) texture combines three channels into a single image:  
- **Red channel**: Ambient Occlusion (AO)  
- **Green channel**: Roughness  
- **Blue channel**: Metallic  

Game engines use these textures to save memory and optimize performance.

---

### 🎨 **How to Use**  
#### 1. 📁 Prepare Your Textures  
- Place all textures in a **single folder**.  
- Name them with **clear suffixes** (e.g., `MyModel_ao.png`, `MyModel_roughness.png`, `MyModel_metallic.png`).  
- **Alternative suffixes**: `ao`, `roughness`, `metallic`, `occlusion`, `metal`, etc.  

**Example folder structure**:  
```
MyModel_ao.png  
MyModel_roughness.png  
MyModel_metallic.png
```

#### 2. ⚙️ Configure Your Settings  
- **Select the folder** containing your textures.  
- **Set suffixes** for each map (e.g., `AO: ao, ambient_occlusion`, `Roughness: roughness, rough`, `Metallic: metallic, metal`).  
- **Optional features**:  
  - 🌙 Dark Theme (for low-light environments)  
  - 📄 Log to File (save output to a `.txt` file)  
  - 🗑️ Delete Obsolete Textures (remove original files after packing)  
  - 🔊 Sound on Finish (notify when done)  

#### 3. 🚀 Start Packing  
- Click **Start** to generate the ORM texture.  
- Output: A new file named `MyModel_ORM.png` will be created in the same folder.  

**Example output**:  
```
MyModel_ORM.png
```

---

### ✅ **Features**  
- Supports **.png** and **.jpg** formats  
- Accepts **multiple suffixes** for each map  
- **Checks for missing/mismatched textures**  
- **Optional logging** to a `.txt` file  
- **Visual themes** (light/dark)  
- **Background processing** with sound notification  
- **Safe operation**: Original textures are not overwritten  

---

### 📁 **Output Location**  
Packed files are saved in the **same folder** as your source textures.  

**Log file example**:  
```
packing_log_20250515.txt
```

---

### 📦 **How to Get the Installer (Windows Only)**  
1. Go to the **Releases** section of the GitHub project.  
2. Download the installer: `ORMTexturePackerInstaller.exe`  
3. Run the installer and follow the instructions.  
4. Launch the app from your desktop or Start menu.  

**Note**: The tool is currently available **only for Windows**.  

---

### 🛠️ **Troubleshooting**  
- **Missing maps?**  
  - Ensure your textures use the correct suffixes (e.g., `ao`, `roughness`, `metallic`).  
- **Different image sizes?**  
  - All three maps must be the same size. Resize them in Photoshop or any image editor.  
- **Nothing happens?**  
  - Check the log file (if enabled) for skipped files or errors.  

---

### 💡 **FAQ**  
- **Can I use other suffixes like `_occlusion` or `_met`?**  
  Yes! Just type your preferred endings in the suffix settings, separated by commas.  
  Example:  
  ```  
  AO: ao, ambient_occlusion, occlusion  
  Metallic: metallic, metal, met  
  ```  

- **Does it overwrite original textures?**  
  No. The tool only creates new `*_ORM.png` files. Your original textures remain untouched.  

---

### 🧩 **Visual Guide to ORM Channels**  
Here’s how the ORM texture channels are mapped:  
- **Red**: Ambient Occlusion (AO)  
- **Green**: Roughness  
- **Blue**: Metallic  

---

### 📌 **What's New**  
- **v1.0.1**: Added support for custom suffixes and optional logging.  
- **v1.0.2**: Improved error handling for mismatched textures.  

---

### 🤝 **Feedback or Ideas?**  
Have a feature request or bug to report? Let us know!  
- **GitHub Issues**: [Link to Issues Page]  
- **Discord Server**: [Link to Community]  
- **Email**: [Support Email]  

---

### 📄 **License**  
This project is open-source and released under the **MIT License**.  

---

### 🚀 **Next Steps**  
- **Explore the GitHub repository** for source code and updates.  
- **Join the community** to share feedback or contribute.  

---

### 🧠 **Why Use This Tool?**  
- **No coding required**: Drag-and-drop simplicity.  
- **Time-saving**: Automates the tedious process of combining textures.  
- **Game-ready**: Optimized for Unreal Engine and Unity.  

---

### 🧩 **Contributing**  
If you're a developer or designer, you can contribute by:  
- Adding support for new file formats.  
- Improving the user interface.  
- Fixing bugs or adding new features.  

**How to contribute**:  
1. Fork the repository.  
2. Create a new branch for your feature.  
3. Submit a pull request.  

---

### 📌 **Final Notes**  
- This tool is designed to **save your time** and **remove technical hurdles**.  
- Focus on your art — let the packer handle the rest!  
