# 3D Fusion AI

[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-r164-green?logo=three.js)](https://threejs.org/)
[![Gemini API](https://img.shields.io/badge/Gemini_API-v1-orange?logo=google)](https://ai.google.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)](https://www.typescriptlang.org/)

An AI-powered web application that transforms a single 2D image into an interactive 3D model. Upload an image, let the AI generate multiple angular views, and watch as they are reconstructed into a 3D object you can view and export.

## ✨ About The Project

This project leverages the power of Google's Gemini and Imagen models to create a seamless workflow for 2D to 3D conversion directly in the browser. It's designed to be a proof-of-concept demonstrating the potential of generative AI in 3D content creation.

The application follows a four-step process:
1.  **Upload:** The user provides a single source image.
2.  **Generate Views:** An AI model describes the object in the image and then generates multiple photorealistic views of it from different angles against a plain background.
3.  **Reconstruct:** Using the generated views, a 3D model is reconstructed via a Visual Hull and Marching Cubes pipeline.
4.  **View & Export:** The final 3D model is displayed in an interactive viewer and can be exported in `.glb` format.

## 🚀 Features

*   **File Upload:** Simple drag-and-drop or file picker for image uploads.
*   **AI-Powered Image Description:** Uses `gemini-2.5-flash` to analyze the uploaded image and generate a text prompt.
*   **Multi-View Generation:** Employs `imagen-4.0-generate-001` to create consistent 360° views of the object.
*   **In-Browser 3D Reconstruction:** Performs 3D reconstruction by creating a Visual Hull from silhouettes and generating a mesh using the Marching Cubes algorithm. Heavy computation is offloaded to a Web Worker to keep the UI responsive.
*   **Interactive 3D Viewer:** Built with `@react-three/fiber`, allowing users to rotate, pan, and zoom the model.
*   **GLB Export:** One-click export of the generated 3D model in the popular glTF binary format.
*   **Responsive UI:** A clean and modern interface built with Tailwind CSS that works across devices.

## 🛠️ Tech Stack

*   **Frontend:** [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/)
*   **3D Graphics:** [Three.js](https://threejs.org/), [@react-three/fiber](https://docs.pmnd.rs/react-three-fiber/getting-started/introduction), [@react-three/drei](https://github.com/pmndrs/drei)
*   **Generative AI:** [@google/genai](https://www.npmjs.com/package/@google/genai) for Google Gemini & Imagen models.
*   **Styling:** [Tailwind CSS](https://tailwindcss.com/)
*   **Concurrency:** [Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)

## 🔧 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You need a modern web browser and a Google AI API key.

*   **Get an API Key:** Create your API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### Installation & Setup

This project is currently set up to run from static files without a build step. However, to manage the API key securely, a local development server is recommended.

1.  **Clone the repository (if you have one):**
    ```sh
    git clone https://github.com/your-repo/3d-fusion-ai.git
    cd 3d-fusion-ai
    ```
2.  **Set up the API Key:**
    The application code expects the API key to be available as `process.env.API_KEY`. The easiest way to provide this is to use a tool like [Vite](https://vitejs.dev/).

    *   Install Node.js and npm if you don't have them.
    *   Create a `.env` file in the project root:
        ```
        VITE_API_KEY=YOUR_GOOGLE_AI_API_KEY
        ```
    *   Update `services/geminiService.ts` to use `import.meta.env.VITE_API_KEY` instead of `process.env.API_KEY`.
    *   Run a development server.

3.  **Running as Static Files (Alternative):**
    If you wish to run `index.html` directly, you must replace `process.env.API_KEY` in `services/geminiService.ts` with your actual API key string. **This is not recommended for security reasons.**

## 📄 Usage

1.  Open the application in your browser.
2.  Click on the "Upload Image" panel to select an image of an object from your computer.
3.  Once the image preview appears, click "Generate 360° Views". The AI will analyze the image and generate four new images from different angles.
4.  After the views are generated, click "Reconstruct 3D Model". A Web Worker will process the images and build the 3D geometry.
5.  The 3D model will appear in the viewer. Use your mouse to rotate, pan, and zoom.
6.  Click "Export GLB" to download the 3D model to your computer.

## 🛣️ Future Roadmap

This project is a work in progress. Here are some of the planned features and improvements:

*   **Implement Real 3D Reconstruction:**
    *   [x] Develop silhouette extraction from the generated 2D views.
    *   [x] Implement the Visual Hull (Space Carving) algorithm to generate a voxel grid.
    *   [x] Use the Marching Cubes algorithm to convert the voxel grid into a mesh (vertices and faces).
    *   [ ] Investigate using WebAssembly (WASM) for performance-critical reconstruction algorithms.
*   **Enhance AI Generation:**
    *   [ ] Allow the user to select the number of views to generate.
    *   [ ] Generate top and bottom views for more complete models.
    *   [ ] Explore AI-based texture and material generation.
*   **Improve User Experience:**
    *   [ ] Add more granular progress indicators for each step.
    *   [ ] Implement 3D model texturing and material options in the viewer.
    *   [ ] Add a gallery of example projects.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License.
