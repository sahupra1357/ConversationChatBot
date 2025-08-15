import { useQuery } from '@tanstack/react-query';

// Use API_BASE from environment or default
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log("Users API_BASE set to:", API_BASE);

interface AdminUserResponse {
  userId: string;
  username?: string;
  isDefault: boolean;
  error?: string;
}

export const getAdminUser = async (): Promise<AdminUserResponse> => {
  try {
    // Add a small delay to ensure the backend is ready
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const url = `${API_BASE}/admin-user`;
    console.log(`Fetching admin user from ${url}`);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      console.error(`Admin user API error: ${response.status}`);
      if (response.status === 404) {
        // If endpoint doesn't exist yet, fall back to env variable
        const defaultUserId = import.meta.env.VITE_DEFAULT_USER_ID || 'admin';
        console.log('Admin user endpoint not found, using default:', defaultUserId);
        return { userId: defaultUserId, isDefault: true };
      }
      
      const errorText = await response.text();
      console.error(`Admin user API error text: ${errorText}`);
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Admin user data:', data);
    return data;
  } catch (error) {
    console.error('Error fetching admin user:', error);
    // Fallback to environment variable
    const defaultUserId = import.meta.env.VITE_DEFAULT_USER_ID || 'admin';
    console.log('Using fallback user ID:', defaultUserId);
    return { userId: defaultUserId, isDefault: true, error: error instanceof Error ? error.message : String(error) };
  }
};

export const useAdminUser = () => {
  return useQuery({
    queryKey: ['adminUser'],
    queryFn: getAdminUser,
    // Don't refetch unnecessarily
    staleTime: 1000 * 60 * 60, // 1 hour
    // Cache for 1 hour
    gcTime: 1000 * 60 * 60,
  });
};
