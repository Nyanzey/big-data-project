import React, { useState } from 'react';
import Header from './Header';
import Footer from './Footer';
import UploadModal from './UploadModal'; // Importa el modal

function Layout({ children }) {
    const [isModalOpen, setIsModalOpen] = useState(false);  // Estado para abrir y cerrar el modal

    // Función para abrir el modal
    const handleUploadClick = () => {
        setIsModalOpen(false);
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
        {/* Pasamos la función handleUploadClick como prop al Header */}
        <Header onUploadClick={handleUploadClick} />

        {/* Área principal del contenido */}
        <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
        </main>

        {/* <Footer /> *}

        {/* Si el modal está abierto, lo renderizamos */}
        {isModalOpen && <UploadModal onClose={() => setIsModalOpen(false)} />}
        </div>
    );
}

export default Layout;
