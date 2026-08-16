const DEFAULT_DATA_PANEL_API_URL = 'https://api.panel.home.enriquegomez.me'

export const DATA_PANEL_API_URL =
  import.meta.env.VITE_DATA_PANEL_API_URL || DEFAULT_DATA_PANEL_API_URL
