import { useEffect, useState } from "react";
import VideoCard from "./VideoCard";
// Importa AMBAS funciones ahora
import { listFilesFromS3, generatePresignedUrlForKey } from "../services/api";

function VideoList({ videos: initialVideos }) {
    // Estado para mantener los videos (incluyendo su URL una vez generada)
    const [videos, setVideos] = useState(initialVideos || []);
    // Estados opcionales para feedback al usuario
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadVideos = async () => {
            setIsLoading(true);
            setError(null);
            try {
                // 1. Obtener la lista de CLAVES de video desde S3
                //const videoKeys = await listFilesFromS3();
                //console.log(videoKeys);

                // 2. Generar una URL prefirmada para CADA clave
                const s3VideoDataPromises = initialVideos.map(async (key) => {
                    try {
                        const presignedUrl = await generatePresignedUrlForKey(key);
                        // Crear el objeto de video con la URL
                        return {
                            id: key, // Usar la clave como ID único
                            title: key.split('/').pop().split('.').slice(0, -1).join('.') || key,
                                                          description: `Video desde S3: ${key}`,
                                                          source: 's3',
                                                          url: presignedUrl // <-- ¡Aquí está la URL!
                        };
                    } catch (urlError) {
                        console.error(urlError.message);
                        // Puedes decidir qué hacer si falla la URL para un video:
                        // - Omitirlo (retornando null y filtrando después)
                        // - Incluirlo pero sin URL o con un estado de error
                        return null; // Omitir videos cuya URL no se pudo generar
                    }
                });

                // Esperar a que todas las promesas de generación de URL se resuelvan
                const resolvedS3VideoData = (await Promise.all(s3VideoDataPromises))
                .filter(video => video !== null); // Filtrar los nulos (errores)

                // 3. Actualizar el estado con los nuevos videos (evitando duplicados)
                setVideos((prevVideos) => {
                    const existingS3Ids = new Set(prevVideos.filter(v => v.source === 's3').map(v => v.id));
                    // Añadir solo los videos de S3 que no estaban ya en el estado
                    const uniqueNewS3Videos = resolvedS3VideoData.filter(sv => !existingS3Ids.has(sv.id));
                    // Combina videos iniciales/existentes con los nuevos únicos de S3
                    return [...prevVideos, ...uniqueNewS3Videos];
                });

            } catch (fetchError) {
                console.error("Error al cargar la lista de videos de S3:", fetchError);
                setError("Error al cargar videos de S3. Intenta de nuevo más tarde.");
            } finally {
                setIsLoading(false);
            }
        };

        loadVideos();
    }, []);

    // Renderizado con estados de carga y error
    if (isLoading) {
        return <p className="text-center mt-8">Cargando videos...</p>;
    }

    if (error) {
        return <p className="text-center mt-8 text-red-600">{error}</p>;
    }

    if (videos.length === 0) {
        return <p className="text-center mt-8">No hay videos para mostrar.</p>;
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-4">
        {videos.map((video) => (
            // Asegúrate que VideoCard usa video.url
            <VideoCard key={video.id} video={video} />
        ))}
        </div>
    );
}

export default VideoList;
