import { useState } from "react";
import VideoList from "../components/VideoList";
import UploadModal from "../components/UploadModal"; // <--- Importar el modal
import { fetchFromInvertedIndex } from "../services/api";

const INITIAL_VIDEOS = [];

function Home() {
  const [videos, setVideos] = useState(INITIAL_VIDEOS);
  const [searchTerm, setSearchTerm] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isButtonLoading, setIsButtonLoading] = useState(false);

  const handleAddVideoClick = () => {
    setIsModalOpen(true);
  };

  const handleUploadVideo = (newVideo) => {
    const newVideoWithId = { ...newVideo, id: videos.length + 1 };
    setVideos([newVideoWithId, ...videos]);
  };

  // Filtrar videos por título
  /* const filteredVideos = videos.filter((video) =>
  video.title.toLowerCase().includes(searchTerm.toLowerCase())
  ); */

  const getVideosFromSearchTerm = async () => {
    if (!searchTerm || searchTerm.length === 0) {
      return;
    }
    setIsButtonLoading(true);
    console.log("Search query: " + searchTerm);
    try {
      const response = await fetchFromInvertedIndex(searchTerm)
      console.log("Home:", response)
      setVideos(response);
    } catch (error) {
      console.error(`Error fetching data: ${error}`);
    }
    setIsButtonLoading(false);
  };

  return (
    <>
    <h1 className="text-5xl font-extrabold text-center text-indigo-800 mb-8">
    Galería de Videos
    </h1>

    {/* Buscador */}
    <div className="flex justify-center mb-6">
    <input
    type="text"
    placeholder="Buscar videos..."
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="w-full max-w-lg p-3 border rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    />
    <button
     onClick={getVideosFromSearchTerm}
     className={!isButtonLoading ?
      "ms-6 inline-block px-5 py-2 bg-blue-600 text-white rounded-md shadow hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2" :
      "ms-6 inline-block px-5 py-2 bg-blue-600 text-white rounded-md shadow hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 animate-spin"
     }
     disabled={isButtonLoading}>
      Buscar
     </button>
    </div>

    <div className="w-full max-w-5xl mx-auto">
    <VideoList initialVideos={videos} />
    </div>

    {/* Botón para añadir video */}
    <button
    type="button"
    onClick={handleAddVideoClick}
    className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-indigo-600 hover:to-blue-500 text-white rounded-full w-16 h-16 flex items-center justify-center shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-75"
    aria-label="Añadir nuevo video"
    >
    <span className="text-3xl font-semibold">+</span>
    </button>

    <UploadModal
    isOpen={isModalOpen}
    onClose={() => setIsModalOpen(false)}
    onUpload={handleUploadVideo}
    />
    </>
  );
}

export default Home;
