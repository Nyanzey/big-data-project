import { useNavigate } from "react-router-dom";

function Header({ onUploadClick }) {
    const navigate = useNavigate()

    return (
        <header className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg">
        <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
        {/* Logo y nombre de la app */}
        <a className="text-2xl font-extrabold text-white tracking-wider"
            href="/"
            onClick={(e) => {
                e.preventDefault()
                navigate("/")
            }}
        >
        Buscador de objetos en videos
        </a>
        </nav>
        </header>
    );
}

export default Header;
