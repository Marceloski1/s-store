import { apiClient } from "@/lib/api/client"
import { unwrap } from "@/lib/api/result"

export const facetService = {
  async get() {
    return unwrap(await apiClient.GET("/catalog/facets"))
  },
}
