import { useState } from "react";
import { fetchFromProcessor, uploadToS3 } from '../services/api';

function UploadModal({ isOpen, onClose, onUpload }) {
    const [videoTitle, setVideoTitle] = useState('');
    const [videoFile, setVideoFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        if (videoTitle && videoFile) {
            try {
                const fileName = videoFile.name;

                await uploadToS3(videoFile, fileName);
                console.log("Archivo subido exitosamente a S3.");

                await fetchFromProcessor(videoTitle, fileName);
                console.log("Solicitud enviada para procesamiento del video.");

                const newVideo = {
                    title: videoTitle,
                    description: `Descripción de ${videoTitle}`,
                    src: URL.createObjectURL(videoFile),
                };
                onUpload(newVideo);

                onClose();

            } catch (error) {
                console.error("Error durante el proceso de subida:", error);
                alert("Hubo un problema al subir o procesar el video. Intenta de nuevo.");
            }
        } else {
            alert("Por favor, ingresa el título y selecciona un archivo de video.");
        }
        setIsLoading(false);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 flex items-center justify-center z-50">
        <div className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-lg transition-all duration-300" />
        <div className="relative bg-white p-8 rounded-2xl shadow-xl max-w-md w-full transform transition-all duration-300 scale-95 hover:scale-100">
        <h2 className="text-3xl font-semibold text-center text-gray-900 mb-6">Subir Nuevo Video</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
        <div>
        <label className="block text-gray-800 font-medium mb-2">Nombre del Video</label>
        <input
        type="text"
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Escribe el título del video"
        value={videoTitle}
        onChange={(e) => setVideoTitle(e.target.value)}
        />
        </div>
        <div>
        <label className="block text-gray-800 font-medium mb-2">Archivo de Video</label>
        <input
        type="file"
        accept="video/mp4"
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        onChange={(e) => setVideoFile(e.target.files[0])}
        />
        </div>

        <div className="flex justify-between items-center">
        <button
        type="button"
        onClick={onClose}
        className="bg-gray-600 text-white px-6 py-3 rounded-lg transition-all duration-300 hover:bg-gray-700 focus:outline-none"
        >
        Cancelar
        </button>
        <button
        type="submit"
        className={!isLoading ? 
            "ml-4 bg-blue-600 text-white px-6 py-3 rounded-lg transition-all duration-300 hover:bg-blue-700 focus:outline-none" :
            "ml-4 bg-blue-600 text-white px-6 py-3 rounded-lg transition-all duration-300 hover:bg-blue-700 focus:outline-none animate-spin"}
        disabled={isLoading}
        >
        Subir
        </button>
        </div>
        </form>
        </div>
        </div>
    );
}

export default UploadModal;
