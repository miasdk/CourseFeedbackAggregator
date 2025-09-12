import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Make Supabase optional - if credentials are missing, create a dummy client
export const supabase = (supabaseUrl && supabaseKey) 
  ? createClient(supabaseUrl, supabaseKey)
  : null as any

// Log warning in development
if (!supabaseUrl || !supabaseKey) {
  console.warn('Supabase credentials not configured - authentication features disabled')
}