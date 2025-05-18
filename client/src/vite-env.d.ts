
interface ImportMetaEnv {
    readonly VITE_API_URL: string;
    // Add more custom env variables here if needed
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}