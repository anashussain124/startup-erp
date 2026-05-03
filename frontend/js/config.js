/**
 * Frontend Configuration
 * Replace these values with your Supabase project credentials.
 */
const CONFIG = {
    SUPABASE_URL: "https://your-project.supabase.co",
    SUPABASE_ANON_KEY: "your-anon-key",
    API_BASE_URL: window.location.origin + "/api"
};

// Initialize Supabase
const supabase = supabase.createClient(CONFIG.SUPABASE_URL, CONFIG.SUPABASE_ANON_KEY);
