export type CryptoProject = {
  id: string
  symbol: string
  name: string
  image?: string | null
  market_cap: number
  fully_diluted_valuation: number
  total_volume: number
  total_value_locked: number
  max_supply: number
  total_supply: number
  preview_listing: boolean
}

export type ApiResponse = { count: number; items: CryptoProject[] }