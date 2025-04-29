function Footer() {
    return (
        <footer className="bg-gradient-to-r from-indigo-700 to-blue-800 text-white mt-auto">
        <div className="container mx-auto px-6 py-6 text-center">
        {/* Texto con un tamaño adecuado y estilo mejorado */}
        <p className="text-lg font-light mb-2">
        © {new Date().getFullYear()} Mi App de Videos. Todos los derechos reservados.
        </p>

        {/* Enlaces o información adicional */}
        <div className="flex justify-center space-x-6">
        <a
        href="#"
        className="text-white hover:text-indigo-200 transition-colors duration-200"
        >
        Política de privacidad
        </a>
        <a
        href="#"
        className="text-white hover:text-indigo-200 transition-colors duration-200"
        >
        Términos de servicio
        </a>
        <a
        href="#"
        className="text-white hover:text-indigo-200 transition-colors duration-200"
        >
        Contacto
        </a>
        </div>
        </div>
        </footer>
    );
}

export default Footer;
