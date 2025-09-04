// types/apiKeys.ts
export interface ApiKey {
    id: string;
    name: string;
    provider: string;
    key_preview: string;
    status: 'active' | 'inactive';
    last_used: string | null;
    created_at: string;
    updated_at: string;
  }
  
  export interface CreateApiKeyRequest {
    name: string;
    provider: string;
    api_key: string;
    base_url: string;
  }
  
  export interface CreateApiKeyResponse {
    id: string;
    name: string;
    provider: string;
    key_preview: string;
    status: 'active';
    created_at: string;
  }