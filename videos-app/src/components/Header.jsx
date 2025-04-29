function Header({ onUploadClick }) {
    return (
        <header className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg">
        <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo y nombre de la app */}
        <div className="text-2xl font-extrabold text-white tracking-wider">
        Mi App de Videos
        </div>

        {/* Menú de navegación */}
        <div className="flex space-x-6">
        <a
        href="#"
        className="text-white hover:text-indigo-300 transition-colors duration-200"
        >
        Inicio
        </a>

        </div>
        </nav>
        </header>
    );
}

export default Header;
