// export default function Footer() {
//     return (
//         <footer className="bg-white shadow-inner p-4 text-center text-sm text-gray-500">
//             © {new Date().getFullYear()} NTUST 英單學習網 Tech Support.
//         </footer>
//     )
// }
// export default function Footer() {
//   return (
//     <footer className="bg-white dark:bg-gray-800 py-4">
//       <div className="max-w-5xl mx-auto text-center text-gray-600 dark:text-gray-300">
//         &copy; {new Date().getFullYear()} NTUST 英單學習網. All rights reserved.
//       </div>
//     </footer>
//   );
// }
export default function Footer() {
    return (
        <footer
            className="bg-gray-100 dark:bg-gray-800 shadow-inner p-4 text-center text-sm text-gray-500 dark:text-gray-300 transition-colors duration-300">
            © {new Date().getFullYear()} NTUST 英簡單. Tech Support.
        </footer>
    )
}