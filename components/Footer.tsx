export default function Footer() {
    const currentYear = new Date().getFullYear();
    return (
        <footer
            className="bg-gray-100 dark:bg-gray-800 shadow-inner p-4 text-center text-sm text-gray-500 dark:text-gray-300 transition-colors duration-300"
        >
            © {currentYear} NTUST 英簡單. Tech Support.
        </footer>
    )
}
