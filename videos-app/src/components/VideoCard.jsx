import { Link } from "react-router-dom";

function VideoCard({ video }) {
    // Es buena práctica añadir una verificación por si el objeto video no es válido
    if (!video || !video.id) {
        console.warn("VideoCard recibió un objeto video inválido:", video);
        return null; // O mostrar un componente de error/placeholder
    }

    // Extrae las propiedades para facilitar la lectura
    const { id, url, title, description } = video;

    return (
        <div className="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 ease-in-out">
        <Link
        // La ruta usa el ID (que es la clave S3). Podría necesitar codificación si la clave tiene caracteres especiales.
        to={`/video/${encodeURIComponent(id)}`}
        // Pasas el objeto video completo en el estado del enlace.
        // Esto es útil porque incluye la 'url' prefirmada,
        // así la página de destino puede usarla directamente sin regenerarla (si no ha expirado).
        state={{ video }}
        >
        {/* Contenedor para la miniatura de video o placeholder */}
        <div className="w-full h-48 bg-gray-200 flex items-center justify-center overflow-hidden"> {/* Añadido contenedor gris como fondo */}
        {url ? (
            <video
            // --- CAMBIO PRINCIPAL AQUÍ ---
            // Usa la URL prefirmada que viene en la propiedad 'url'
            src={url}
            // --- FIN DEL CAMBIO ---
            className="w-full h-full object-cover" // Ajustado para llenar el contenedor
            controls={false} // Sin controles para la miniatura
            muted // Silenciado es bueno para miniaturas/previsualizaciones
            preload="metadata" // Carga solo metadatos (duración, dimensiones) - eficiente
            // Opcional: podrías querer añadir un 'poster' si tienes imágenes miniatura generadas
            // poster={video.thumbnailUrl} // Necesitarías añadir thumbnailUrl al objeto video
            // Hacemos que el video en sí no sea interactivo, ya que todo el card es un enlace
            style={{ pointerEvents: 'none' }}
            />
        ) : (
            // Mostrar un placeholder si la URL no está disponible
            <div className="text-center text-gray-500 px-2">
            Vista previa no disponible
            </div>
        )}
        </div>

        {/* Información del Video */}
        <div className="p-4">
        <h2
        className="text-xl font-semibold text-gray-800 truncate hover:text-blue-600 transition-colors duration-300"
        title={title} // Añadir title por si el texto se trunca
        >
        {/* Mostrar un título por defecto si no existe */}
        {title || "Video sin título"}
        </h2>
        <p className="text-gray-600 text-sm mt-2 line-clamp-3 hover:text-gray-800 transition-colors duration-300">
        {/* Mostrar cadena vacía si no hay descripción */}
        {description || ""}
        </p>
        </div>
        </Link>
        </div>
    );
}

export default VideoCard;
