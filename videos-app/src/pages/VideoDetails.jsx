import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";

function VideoDetails() {
  const { state } = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!state?.video) {
      console.warn("VideoDetails: No se encontró state.video. Redirigiendo...");
      navigate("/");
    }
  }, [state, navigate]);


  if (!state?.video) {
    return null;
  }

  const { id, url, title, description, seconds } = state.video;
  if (!url) {
    console.error("VideoDetails: El objeto video no contiene una URL válida.", state.video);
    return (
      <div className="min-h-screen bg-gray-100 p-6 flex items-center justify-center">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6 text-center">
      <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
      <p className="text-gray-700">No se pudo encontrar la URL para este video.</p>
      <button
      onClick={() => navigate("/")}
      className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
      Volver a la lista
      </button>
      </div>
      </div>
    );
  }

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    const paddedSeconds = remainingSeconds.toString().padStart(2, '0');
    return `${minutes}:${paddedSeconds}`;
  }

  const handleTimestamp = (e, seg) => {
    e.preventDefault();
    const video = document.getElementById("video");
    if (video) {
      video.currentTime = seg;
    } else {
      console.error("No se encontró el elemento de video.");
    }
  }


  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4 sm:px-6 lg:px-8"> {/* Padding ajustado */}
    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-2xl overflow-hidden">
    <div className="bg-black">
    <video
      id="video"
      key={id}
      className="w-full aspect-video"
      preload="auto"
      controls>
      <source src={url} type="video/mp4" />
    </video>
  </div>

  <div className="p-6 md:p-8">
  <h1 className="text-3xl sm:text-4xl font-bold mb-4 text-gray-900 break-words">
  {title || "Video sin título"}
  </h1>
  <p className="text-base sm:text-lg text-gray-700 leading-relaxed">
  {description || "No hay descripción disponible."}
  </p>
  <div className="text-base sm:text-lg text-gray-700 leading-relaxed">
    {seconds.map((seg) => (
      <a href="#" onClick={(e) => handleTimestamp(e, seg)} className="pe-2 text-blue-500 hover:underline">{formatTime(seg)}</a>
    ))}
  </div>
  <button
  onClick={() => navigate(-1)}
  className="mt-6 inline-block px-5 py-2 bg-blue-600 text-white rounded-md shadow hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
  >
  ← Volver
  </button>
  </div>
  </div>
  </div>
  );
}

export default VideoDetails;
