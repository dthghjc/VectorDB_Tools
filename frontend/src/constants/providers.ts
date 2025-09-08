// constants/providers.ts

/**
 * 供应商UI配置映射（仅用于展示层配置）
 * 真实的供应商列表从后端 /api/v1/keys/providers 获取
 */
export const PROVIDER_UI_CONFIG: Record<string, {
  label: string;
}> = {
  "openai": {
    label: "OpenAI"
  },
  "siliconflow": {
    label: "SiliconFlow"
  },
  "bce-qianfan": {
    label: "BCE-Qianfan"
  },
  "nvidia-nim": {
    label: "Nvidia NIM"
  },
  "ollama": {
    label: "Ollama"
  }
};

/**
 * 根据供应商获取显示标签
 */
export function getProviderLabel(provider: string): string {
  return PROVIDER_UI_CONFIG[provider]?.label || provider;
}

/**
 * 将后端供应商列表转换为前端选项格式
 */
export function transformProvidersToOptions(providers: string[]) {
  return providers.map(provider => ({
    value: provider,
    label: getProviderLabel(provider)
  }));
}
